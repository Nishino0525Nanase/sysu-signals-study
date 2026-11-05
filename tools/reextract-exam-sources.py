#!/usr/bin/env python3
"""Re-render the exact published exam-page set; no OCR replacement or generated detail.
Requires: PyMuPDF (fitz), Pillow. Outputs full pages, 600px thumbs and manifest.json.
Run: python reextract-exam-sources.py --project-root /.../sysu-signals-study --output /.../tmp/exam-sources-hq
"""
import argparse, hashlib, json, math, os, re
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import fitz

def atomic_webp(im, path, quality):
    tmp=path.with_name(path.name+'.tmp')
    im.save(tmp,format='WEBP',quality=quality,method=6,exact=True)
    os.replace(tmp,path)

def dominant_raster(page):
    candidates=[]
    area=page.rect.width*page.rect.height
    for info in page.get_image_info():
        if min(info['width'],info['height'])<300: continue
        rect=fitz.Rect(info['bbox']) & page.rect
        coverage=max(0,rect.width)*max(0,rect.height)/area
        if coverage<0.25: continue
        a,b,c,d,e,f=info['transform']
        sx=info['width']/max(math.hypot(a,b),1e-9)
        sy=info['height']/max(math.hypot(c,d),1e-9)
        candidates.append((coverage,min(sx,sy),info))
    return max(candidates,key=lambda x:x[0]) if candidates else None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--upload',type=Path)
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[2]/'tmp/exam-sources-hq')
    ap.add_argument('--dpi',type=int,default=300)
    ap.add_argument('--max-edge',type=int,default=3000)
    ap.add_argument('--thumb-edge',type=int,default=600)
    ap.add_argument('--quality',type=int,default=96)
    ap.add_argument('--resume',action='store_true',help='Reuse full-size files only when dimensions match this render scale.')
    ap.add_argument('--allow-raster-upscale',action='store_true',help='Not recommended: only interpolates existing pixels; adds no detail.')
    args=ap.parse_args()
    olddir=args.project_root/'dist/sources';upload=args.upload or args.project_root.parent/'upload'
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'thumbs').mkdir(exist_ok=True)
    documents={};rows=[]
    for old in sorted(olddir.glob('*.webp')):
        match=re.fullmatch(r'(20\d\d)_(\d+)\.webp',old.name)
        if not match: continue
        year,number=map(int,match.groups())
        if year not in documents:
            paths=sorted(upload.glob(f'{year}*.pdf*'))
            if len(paths)!=1: raise ValueError(f'Ambiguous source PDF for {year}: {len(paths)}')
            documents[year]=(paths[0],fitz.open(paths[0]))
        pdf,doc=documents[year];page=doc[number-1]
        desired=min(args.dpi/72,args.max_edge/max(page.rect.width,page.rect.height))
        raster=dominant_raster(page)
        native=raster[1] if raster else None
        scale=desired if args.allow_raster_upscale or native is None else min(desired,native)
        dest=args.output/old.name;im=None
        if args.resume and dest.exists():
            try:
                with Image.open(dest) as cached:
                    expected=(math.ceil(page.rect.width*scale),math.ceil(page.rect.height*scale))
                    if all(abs(a-b)<=1 for a,b in zip(cached.size,expected)): im=cached.convert('RGB')
            except Exception: pass
        if im is None:
            pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csRGB,alpha=False)
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            # Mild deterministic processing only: no thresholding, stroke synthesis, denoising or OCR replacement.
            im=ImageEnhance.Contrast(im).enhance(1.025)
            im=im.filter(ImageFilter.UnsharpMask(radius=0.55,percent=65,threshold=3))
            atomic_webp(im,dest,args.quality)
        thumb=im.copy();thumb.thumbnail((args.thumb_edge,args.thumb_edge),Image.Resampling.LANCZOS)
        td=args.output/'thumbs'/old.name;atomic_webp(thumb,td,88)
        try:
            with Image.open(old) as previous: oldsize=list(previous.size)
        except Exception:
            oldsize=None
        outbytes=dest.read_bytes()
        status='vector_or_mixed'
        if native is not None: status='native_raster_limited' if native<desired-0.01 else 'high_resolution_raster'
        note='原页矢量/文字可在目标尺寸重渲染。' if native is None else ('原件栅格像素限制；没有放大插值或伪造细节。' if status=='native_raster_limited' else '原始嵌图足以支持本次重渲染尺寸。')
        row={'file':old.name,'year':year,'pdfPage':number,'sourcePdf':pdf.name,'pagePoints':[round(page.rect.width,2),round(page.rect.height,2)],'oldDimensions':oldsize,'oldBytes':old.stat().st_size,'dimensions':[im.width,im.height],'bytes':len(outbytes),'sha256':hashlib.sha256(outbytes).hexdigest(),'thumbnail':f'thumbs/{old.name}','thumbnailDimensions':[thumb.width,thumb.height],'thumbnailBytes':td.stat().st_size,'effectiveRenderDpi':round(scale*72,1),'renderScale':round(scale,5),'sourceKind':status,'note':note}
        if raster:
            row['dominantEmbeddedPixels']=[raster[2]['width'],raster[2]['height']]
            row['dominantEmbeddedCoverage']=round(raster[0],4)
            row['nativePageScale']=round(native,5)
        rows.append(row);print(json.dumps({'file':old.name,'size':row['dimensions'],'kind':status},ensure_ascii=False),flush=True)
    manifest={'settings':{'dpiTarget':args.dpi,'maxEdge':args.max_edge,'avoidRasterUpscale':not args.allow_raster_upscale,'webpQuality':args.quality,'thumbnailMaxEdge':args.thumb_edge,'contrast':1.025,'unsharp':{'radius':0.55,'percent':65,'threshold':3}},'count':len(rows),'oldTotalBytes':sum(r['oldBytes'] for r in rows),'fullTotalBytes':sum(r['bytes'] for r in rows),'thumbnailTotalBytes':sum(r['thumbnailBytes'] for r in rows),'pages':rows,'limitations':['源PDF缺失或被裁切的公式不能通过提高DPI恢复；不作内容补绘。','较低清的2021、2023、2024、2026等原件只能保留现有数学笔画，输出像素多不代表信息更多。','仅重渲染现有sources文件集合：2025重复第3页仍不加入；2026只取题面前两页。','页尺寸有时以像素数作为PDF点数写入，effectiveRenderDpi仅为PDF坐标比例，不能据此推断纸面扫描精度。']}
    temp=args.output/'manifest.json.tmp';temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));os.replace(temp,args.output/'manifest.json')
    for _,doc in documents.values():doc.close()
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('pages','limitations')},ensure_ascii=False))
if __name__=='__main__':main()
