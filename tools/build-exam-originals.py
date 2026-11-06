#!/usr/bin/env python3
"""Extract verified question regions from the supplied exam scans, without resizing."""
from pathlib import Path
import hashlib, json, os
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
locations = json.loads((ROOT / 'content/exam-original-locations.json').read_text())
out = ROOT / 'content/exam-originals'
out.mkdir(exist_ok=True)
source_info, entries = {}, []

for entry in locations:
    excerpts = []
    for index, region in enumerate(entry['excerpts'], 1):
        relative = f"sources/{entry['year']}_{region['page']}.webp"
        source = ROOT / 'dist' / relative
        if relative not in source_info:
            with Image.open(source) as image:
                source_info[relative] = {'path': relative, 'width': image.width, 'height': image.height, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        with Image.open(source) as image:
            rect = region['rect']
            assert len(rect) == 4 and all(isinstance(v, int) for v in rect), entry['id']
            x0, y0, x1, y1 = rect
            assert 0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height, (entry['id'], rect, image.size)
            crop = image.convert('RGB').crop(rect)
        name = f"{entry['id']}-{index:02}.webp"
        target = out / name
        temp = out / (name + '.tmp')
        crop.save(temp, format='WEBP', lossless=True, method=6, exact=True)
        os.replace(temp, target)
        with Image.open(target) as checked:
            assert checked.convert('RGB').tobytes() == crop.tobytes(), name
        excerpts.append({'path': 'sources/questions/' + name, 'pdfPage': region['page'], 'rect': rect, 'width': crop.width, 'height': crop.height, 'bytes': target.stat().st_size, 'sourcePath': relative, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    entries.append({'id': entry['id'], 'year': entry['year'], 'ref': entry['ref'], 'note': entry.get('note', ''), 'displayNote': entry.get('displayNote', ''), 'verifiedFrom': entry.get('verifiedFrom', ''), 'excerpts': excerpts})

result = {'version': 1, 'policy': '按所供原卷实际像素无损裁剪，保留跨页题面、公共条件与原图，不用辅助题意替代原题。', 'sourcePages': list(source_info.values()), 'questions': entries}
destination = ROOT / 'content/exam-originals.json'
temporary = destination.with_suffix('.json.tmp')
temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2))
os.replace(temporary, destination)
print(json.dumps({'questions': len(entries), 'excerpts': sum(len(e['excerpts']) for e in entries), 'bytes': sum(e['bytes'] for q in entries for e in q['excerpts'])}))
