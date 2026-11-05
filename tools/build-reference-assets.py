"""Render verified excerpts from the user-supplied textbook PDF.

Only selected exercise and concept regions are exported. Coordinates and source
SHA are retained for review; the complete textbook is never copied to dist.
Requires PyMuPDF and Pillow. Example:
  python tools/build-reference-assets.py --textbook '/path/book.pdf'
"""
import argparse,hashlib,json,os,re
from pathlib import Path
import fitz
from PIL import Image,ImageOps,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--textbook',required=True)
parser.add_argument('--locations',default=str(ROOT/'content/reference-locations.json'))
args=parser.parse_args()
pdf=Path(args.textbook);doc=fitz.open(pdf)
locations=json.loads(Path(args.locations).read_text())
assets=ROOT/'content/references/book';assets.mkdir(parents=True,exist_ok=True)
render_temp=ROOT/'android/build/reference-render';render_temp.mkdir(parents=True,exist_ok=True)
source_hash=hashlib.sha256(pdf.read_bytes()).hexdigest()
old_path=ROOT/'content/textbook-links.json'
old=json.loads(old_path.read_text()) if old_path.exists() else {}
old_entries={e['id']:e for key in ['exercises','concepts','relationExcerpts'] for e in old.get(key,[])}

def write_json(p,value):
    t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');os.replace(t,p)

def density(page):
    """Cap raster scans at actual sampling density instead of inventing detail."""
    best=None
    for im in page.get_images(full=True):
        for r in page.get_image_rects(im[0]):
            area=r.width*r.height
            if area>page.rect.width*page.rect.height*.65:
                value=min(im[2]/r.width,im[3]/r.height)
                if best is None or area>best[0]:best=(area,value)
    return best[1] if best else None

def render(entry,kind):
    previous=old_entries.get(entry['id'])
    if old.get('book',{}).get('sha256')==source_hash and previous and previous.get('crops')==entry.get('crops') and all((ROOT/'content'/e[p]).is_file() and (ROOT/'content'/e[p]).stat().st_size>0 for e in previous.get('excerpts',[]) for p in ['path','thumb']):
        return {**entry,'excerpts':previous['excerpts']}
    excerpts=[]
    for i,crop in enumerate(entry.get('crops',[]),1):
        number=crop['page'];page=doc[number-1];r=crop['rect']
        assert len(r)==4 and 0<=r[0]<r[2]<=1 and 0<=r[1]<r[3]<=1,(entry['id'],r)
        clip=fitz.Rect(r[0]*page.rect.width,r[1]*page.rect.height,r[2]*page.rect.width,r[3]*page.rect.height)
        native=density(page);scale=min(300/72,native) if native else 300/72
        scale=min(scale,3000/max(clip.width,clip.height))
        pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,colorspace=fitz.csGRAY,alpha=False)
        image=Image.frombytes('L',(pix.width,pix.height),pix.samples)
        # Gentle contrast and edge restoration preserve the source's math strokes.
        image=ImageOps.autocontrast(image,cutoff=.1).filter(ImageFilter.UnsharpMask(radius=.55,percent=65,threshold=3))
        key=re.sub(r'[^A-Za-z0-9._-]','-',entry['id'])+f'-{i:02}'
        destination=assets/(key+'.webp');temp=render_temp/(key+'.tmp.webp')
        image.save(temp,'WEBP',lossless=True,method=6);os.replace(temp,destination)
        thumb=image.copy();thumb.thumbnail((640,1600),Image.Resampling.LANCZOS)
        thumbpath=assets/(key+'-thumb.webp');temp=render_temp/(key+'-thumb.tmp.webp')
        thumb.save(temp,'WEBP',quality=90,method=6);os.replace(temp,thumbpath)
        excerpts.append({'path':'references/book/'+destination.name,'thumb':'references/book/'+thumbpath.name,
            'width':image.width,'height':image.height,'pdfPage':number,
            'printPage':crop.get('printPage',number-22),
            'caption':crop.get('caption',entry.get('title') or entry.get('bookQuestion','原书摘图')),
            'rect':r,'nativePixelsPreserved':native is not None})
    return {**entry,'excerpts':excerpts}

result={'book':{'id':'OPP-CN2','title':'信号与系统（第二版）','authors':'A. V. Oppenheim、A. S. Willsky、S. H. Nawab','translator':'刘树棠',
    'edition':'上传的中文版第二版','pdfPages':len(doc),'sha256':source_hash,
    'paginationNote':'书页指页面印出的页码；PDF页包含封面与目录，逐项另列。'},
    'exercises':[render(e,'exercise') for e in locations['exercises']],
    'concepts':[render(e,'concept') for e in locations['concepts']],
    'relationExcerpts':[render(e,'relation') for e in locations.get('relationExcerpts',[])],
    'relations':locations.get('relations',[]),
    'auditNotes':locations.get('auditNotes',[])}
write_json(ROOT/'content/textbook-links.json',result)
print(json.dumps({'exercises':len(result['exercises']),'concepts':len(result['concepts']),
    'images':sum(len(result[k][i]['excerpts']) for k in ['exercises','concepts','relationExcerpts'] for i in range(len(result[k]))),
    'bytes':sum(p.stat().st_size for p in assets.glob('*.webp'))}))
