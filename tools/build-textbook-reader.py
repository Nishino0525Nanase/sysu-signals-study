#!/usr/bin/env python3
"""Build a complete, native-resolution reader for the supplied Chinese scan.

No OCR, generative restoration, cropping, deskewing, or enlargement is applied.
Single full-page one-bit scans are decoded at their original dimensions.
Composite pages are rendered at the scan's original 300 dpi so inset images
are retained. Covers use their actual image pixel density rather than 300 dpi.
All image writes and the PDF write are staged, decoded, then atomically moved.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from uuid import uuid4

import fitz
from PIL import Image, ImageOps
from pypdf import PdfReader


PROJECT = Path(__file__).resolve().parents[1]
SOURCE_DEFAULT = PROJECT.parent / "upload" / (
    "信号与系统 第二版 (艾伦V.奥本海姆) "
    "(z-library.sk, 1lib.sk, z-lib.sk).pdf"
)
PDF_FILENAME = "oppenheim-signals-systems-2e-zh-native-hd.pdf"
_DOC = None
_STAGE = None
_TARGET = None
_METHOD = 6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def init_worker(source: str, stage: str, target: str, method: int) -> None:
    global _DOC, _STAGE, _TARGET, _METHOD
    _DOC = fitz.open(source)
    _STAGE = Path(stage)
    _TARGET = Path(target)
    _METHOD = method


def native_page(page_number: int) -> tuple[Image.Image, str]:
    page = _DOC[page_number - 1]
    images = page.get_images(full=True)
    if len(images) == 1 and images[0][4] == 1:
        xref = images[0][0]
        positions = page.get_image_rects(xref, transform=True)
        full = (
            len(positions) == 1
            and max(abs(a - b) for a, b in zip(positions[0][0], page.rect)) < 0.01
        )
        matrix = positions[0][1] if positions else None
        unrotated = matrix is not None and abs(matrix.b) < 1e-5 and abs(matrix.c) < 1e-5
        if full and unrotated and not page.rotation and not page.get_text().strip() and not page.get_drawings():
            raw = _DOC.extract_image(xref)
            with Image.open(io.BytesIO(raw["image"])) as native:
                native.load()
                # A stencil ImageMask is not an ordinary grayscale image:
                # extraction alone may expose the mask's inverse polarity.
                image = native.convert("L")
            if image.size != (images[0][2], images[0][3]):
                raise ValueError(f"Native image size changed on page {page_number}")
            # Calibrate EVERY single-bit page against the actual PDF renderer.
            # A hard classification is used only to resolve the original 0/255
            # mask semantics, never to generate or smooth character strokes.
            pix = page.get_pixmap(
                matrix=fitz.Matrix(image.width / page.rect.width, image.height / page.rect.height),
                colorspace=fitz.csGRAY,
                alpha=False,
            )
            reference = Image.frombytes("L", (pix.width, pix.height), pix.samples)
            binary_reference = reference.point(lambda value: 255 if value >= 128 else 0)
            if image.tobytes() != binary_reference.tobytes():
                inverted = ImageOps.invert(image)
                if inverted.tobytes() != binary_reference.tobytes():
                    # A front-matter page has a fractionally translated image
                    # rectangle. Keep the actual original PDF page canvas at
                    # the source image's dimensions, rather than thresholding
                    # or altering that page to force a binary comparison.
                    return reference, "native-canvas-render"
                image = inverted
            return image, "native-one-bit"

    if page_number in (1, 2) and len(images) == 1:
        scan = images[0]
        bounds = page.get_image_rects(scan[0])[0]
        # The small white page margin is retained without enlarging the cover.
        density = min(scan[2] / bounds.width, scan[3] / bounds.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(density, density), colorspace=fitz.csRGB, alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples), "native-cover-density"

    # Some textbook pages contain a one-bit base plus grayscale inset graphics.
    # Rendering the entire page retains the overlays; extracting the base alone
    # would silently omit their figures.
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), colorspace=fitz.csRGB, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples), "full-page-300dpi"


def build_image(page_number: int) -> dict:
    image, strategy = native_page(page_number)
    name = f"page-{page_number:03}.webp"
    staging = _STAGE / (name + ".part")
    target = _TARGET / name
    image.save(staging, format="WEBP", lossless=True, method=_METHOD, exact=True)
    if staging.stat().st_size == 0:
        raise ValueError(f"Empty encoded image on page {page_number}")
    with Image.open(staging) as check:
        check.load()
        if check.size != image.size:
            raise ValueError(f"Encoded dimensions differ on page {page_number}")
        if check.convert(image.mode).tobytes() != image.tobytes():
            raise ValueError(f"Lossless pixel comparison failed on page {page_number}")
    os.replace(staging, target)
    record = {
        "pdfPage": page_number,
        "printPage": page_number - 22 if 23 <= page_number <= 627 else None,
        "path": f"references/textbook/{name}",
        "width": image.width,
        "height": image.height,
        "bytes": target.stat().st_size,
    }
    image.close()
    return {"page": record, "strategy": strategy}


def image_streams(doc: fitz.Document, page: int) -> list[tuple]:
    """Check the optimized PDF kept the original encoded scans unchanged."""
    records = []
    for entry in doc[page].get_images(full=True):
        raw = doc.xref_stream_raw(entry[0])
        records.append((entry[2], entry[3], entry[4], hashlib.sha256(raw).hexdigest()))
    return records


def build_pdf(source: Path, stage: Path, output_dir: Path) -> dict:
    doc = fitz.open(source)
    original_toc = doc.get_toc()
    original_rects = [tuple(page.rect) for page in doc]
    original_streams = [image_streams(doc, i) for i in range(len(doc))]
    # Visual inspection verified: PDF 23=printed 1, PDF 627=printed 605.
    # PDF 628 is a file-information sheet, not textbook page 606.
    # Use actual UTF-16BE PDF text strings. The installed PyMuPDF page-label
    # helper wraps non-ASCII hex output in a second string layer, so it cannot
    # be used to author Chinese label prefixes safely in this environment.
    def pdf_string(value: str) -> str:
        return "<FEFF" + value.encode("utf-16-be").hex().upper() + ">"

    doc.xref_set_key(
        doc.pdf_catalog(),
        "PageLabels",
        "<< /Nums [ "
        "0 << /P " + pdf_string("前置-") + " /S /D /St 1 >> "
        "22 << /S /D /St 1 >> "
        "627 << /P " + pdf_string("文件信息") + " >> ] >>",
    )
    metadata = doc.metadata
    metadata.update({
        "title": "信号与系统（第二版）中文版 · 原生高清整理版",
        "subject": "完整原始扫描；图像无重采样；保留书签、页面尺寸；新增页码标签",
        "keywords": "信号与系统,奥本海姆,中文版,原生扫描,页面标签",
        "modDate": "D:" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "+00'00'",
    })
    doc.set_metadata(metadata)
    temporary = stage / (PDF_FILENAME + ".part")
    # Keep original CCITT/JPEG streams. Do not rasterize or resample this PDF.
    doc.save(temporary, garbage=4, deflate=True, clean=False, incremental=False)
    doc.close()
    with fitz.open(temporary) as check:
        if len(check) != 628 or check.get_toc() != original_toc:
            raise ValueError("PDF page count or original bookmarks changed")
        if [tuple(page.rect) for page in check] != original_rects:
            raise ValueError("PDF page dimensions changed")
        for i in range(len(check)):
            if image_streams(check, i) != original_streams[i]:
                raise ValueError(f"Original encoded image stream changed on PDF page {i + 1}")
    # Verify labels through a second PDF implementation, including Unicode.
    labels = PdfReader(temporary).page_labels
    if [labels[p - 1] for p in [1, 22, 23, 627, 628]] != ["前置-1", "前置-22", "1", "605", "文件信息"]:
        raise ValueError("Unexpected standard PDF page labels")
    # Avoid accidentally shipping a rasterized or bloated version.
    if temporary.stat().st_size > source.stat().st_size * 1.10:
        raise ValueError("PDF grew more than 10%; original streams should be retained")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / PDF_FILENAME
    os.replace(temporary, target)
    return {"filename": PDF_FILENAME, "bytes": target.stat().st_size, "sha256": sha256(target)}


def atomic_json(path: Path, data: dict, stage: Path) -> None:
    temporary = stage / (path.name + ".part")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--webp-method", type=int, choices=range(7), default=6)
    args = parser.parse_args()
    source = args.source.resolve()
    target = PROJECT / "content" / "references" / "textbook"
    metadata_path = PROJECT / "content" / "textbook-reader.json"
    output_dir = PROJECT / "android" / "build" / "textbook-reader"
    stage = output_dir / ("run-" + uuid4().hex)
    stage.mkdir(parents=True)
    target.mkdir(parents=True, exist_ok=True)
    started = monotonic()
    with fitz.open(source) as doc:
        if len(doc) != 628 or len(doc.get_toc()) != 302:
            raise ValueError("This source differs from the visually audited 628-page edition")
        toc = [{"level": level, "title": title, "pdfPage": page} for level, title, page in doc.get_toc()]

    pages, strategies = [], {}
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=init_worker,
        initargs=(str(source), str(stage), str(target), args.webp_method),
    ) as pool:
        pending = [pool.submit(build_image, page) for page in range(1, 629)]
        for index, future in enumerate(as_completed(pending), start=1):
            result = future.result()
            pages.append(result["page"])
            strategies[result["strategy"]] = strategies.get(result["strategy"], 0) + 1
            if index % 25 == 0 or index == 628:
                print(json.dumps({"images": index, "total": 628, "elapsedSeconds": round(monotonic() - started, 1)}), flush=True)
    pages.sort(key=lambda page: page["pdfPage"])

    # Second, independent full-file decode pass after every atomic move.
    for record in pages:
        path = PROJECT / "content" / record["path"]
        if path.stat().st_size != record["bytes"] or record["bytes"] <= 0:
            raise ValueError(f"Missing or truncated final image: {path}")
        with Image.open(path) as image:
            image.load()
            if image.size != (record["width"], record["height"]):
                raise ValueError(f"Wrong final image dimensions: {path}")
    print(json.dumps({"allImageDecodes": 628, "strategies": strategies, "imageBytes": sum(p["bytes"] for p in pages)}), flush=True)

    download = build_pdf(source, stage, output_dir)
    quality = (
        "完整628页，保留全部原页面和302条原书签。"
        f"{strategies.get('native-one-bit', 0)}页单幅1位黑白扫描直接保留原生像素，"
        "逐页对照原PDF渲染校准ImageMask黑白极性，不灰度化、不锐化、不放大；"
        f"{strategies.get('native-canvas-render', 0)}页前置页因原PDF图像存在亚像素位置，"
        "以原图像素尺寸整页渲染以保留真实页面布局，不为强求二值化而改写笔画；"
        "29页含灰度插图的复合页面以原扫描300dpi整页合成，"
        "避免漏掉叠加图形；2页封面按实际约158dpi图像密度保留完整页面，"
        "末尾文件信息页按300dpi渲染。网页图像为逐像素核验的无损WebP。"
        "下载PDF保留原始CCITT/JPEG图像流、页面尺寸及书签，仅优化文件结构并新增页码标签；"
        "印刷1–605对应PDF23–627，封面前置页及末尾信息页不冒标正文页码。"
        "未使用生成式修复、文字重绘、超分辨率、裁切或盲目放大。"
    )
    metadata = {
        "id": "oppenheim-signals-systems-2e-zh",
        "title": "奥本海姆《信号与系统》第二版中文版 · 原生高清阅读",
        "sourceSha256": sha256(source),
        "pdfPageCount": 628,
        "printPageOffset": 22,
        "pages": pages,
        "toc": toc,
        "qualityNote": quality,
        "download": download,
    }
    atomic_json(metadata_path, metadata, stage)
    report = {
        "pdfPages": 628,
        "printPages": 605,
        "bookmarks": len(toc),
        "imageBytes": sum(page["bytes"] for page in pages),
        "imageMinBytes": min(page["bytes"] for page in pages),
        "imageMaxBytes": max(page["bytes"] for page in pages),
        "strategies": strategies,
        "allImageDecodes": 628,
        "pixelComparisons": 628,
        "pdfRenderedPolarityCalibrations": strategies.get("native-one-bit", 0),
        "pdfOriginalImageStreamsUnchanged": True,
        "pdfPageDimensionsUnchanged": True,
        "download": download,
        "elapsedSeconds": round(monotonic() - started, 1),
    }
    atomic_json(output_dir / "build-report.json", report, stage)
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
