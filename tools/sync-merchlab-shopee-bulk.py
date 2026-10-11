#!/usr/bin/env python3
"""Import Shopee PH three-file mass-update exports into MerchLab's read-only storefront catalog.
Only standard library. Does NOT upload/edit anything on Shopee.
Usage: python3 tools/sync-merchlab-shopee-bulk.py basic.xlsx sales.xlsx media.xlsx
"""
import sys, os, json, re, zipfile, xml.etree.ElementTree as ET, pathlib, collections, datetime, urllib.parse
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'public'/'merchlab'
def excel_rows(filename):
    with zipfile.ZipFile(filename) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings=[''.join(x.itertext()) for x in root.findall(NS+'si')]
        doc=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        for row in doc.findall('.//'+NS+'sheetData/'+NS+'row'):
            if int(row.get('r',0))<7:continue
            data={}
            for cell in row.findall(NS+'c'):
                col=re.match(r'[A-Z]+',cell.get('r','')).group()
                node=cell.find(NS+'v')
                val='' if node is None else node.text or ''
                if cell.get('t')=='s' and val:val=strings[int(val)]
                elif cell.get('t')=='inlineStr':
                    inline=cell.find(NS+'is')
                    val=''.join(inline.itertext()) if inline is not None else ''
                data[col]=val
            if str(data.get('A','')).isdigit():yield data
def guard(cond,msg):
    if not cond:raise ValueError(msg)
def price(raw):
    try:return float(raw)
    except (TypeError,ValueError):return None
def trimname(raw):
    return re.sub(r'^\s*\[Merch\s*Lab\]\s*','',raw,flags=re.I).strip()
def category(raw,name):
    cat=raw.lower();title=name.lower()
    if 'bags/' in cat or 'travel bags' in cat or re.search(r'\b(bag|pouch|tote|sling|handbag|wallet)\b',title):
        return 'Bags'
    if 'earring' in cat:return 'Earrings'
    if 'necklace' in cat:return 'Necklaces'
    if 'ring' in cat and 'earring' not in cat:return 'Rings'
    if 'bracelet' in cat or 'bangle' in cat:return 'Bracelets'
    if 'fashion accessories' in cat:return 'Accessories'
    if any(x in cat for x in ['clothes/','apparels/','women clothes','men clothes','fabric/']):return 'Fashion'
    if 'beauty/' in cat:return 'Accessories'
    if re.search(r'\b(earring|necklace|pendant|bangle|bracelet|ring|anklet|rosary)\b',title):return 'Accessories'
    return 'Accessories'
def urlok(raw):
    if not raw:return False
    u=urllib.parse.urlparse(raw)
    return u.scheme=='https' and u.hostname in ('cf.shopee.ph','down-ph.img.susercontent.com','down-ph.img.susercontent.com')
def uniq(seq):
    return list(dict.fromkeys(x for x in seq if x))
def main(basic_file,sales_file,media_file):
    basic=list(excel_rows(basic_file));sales=list(excel_rows(sales_file));media=list(excel_rows(media_file))
    guard(all(len(x)>0 for x in (basic,sales,media)),'At least one input workbook is empty')
    basemap={r['A']:r for r in basic};mediamap={r['A']:r for r in media}
    guard(len(basemap)==len(basic),'Duplicate IDs in basic export')
    guard(len(mediamap)==len(media),'Duplicate IDs in media export')
    guard(set(basemap)==set(mediamap),'Basic/media export ID sets differ')
    sell=collections.defaultdict(list)
    for r in sales:sell[r['A']].append(r)
    guard(set(sell)==set(basemap),'Sales export ID set differs from basic export')
    previous=[]
    for i in range(1,9):previous.extend(json.loads((OUT/f'products-{i}.json').read_text(encoding='utf-8')))
    oldids={str(r['id']) for r in previous}
    now=datetime.date.today().isoformat()
    products=[]
    for pid,b in basemap.items():
        m=mediamap[pid];variations=sell[pid]
        name=trimname(b.get('C',''))
        guard(bool(name),f'Missing title for {pid}')
        cover=m.get('E','')
        photos=uniq([cover]+[m.get(chr(ord('F')+i),'') for i in range(8)])
        guard(bool(cover) and all(urlok(u) for u in photos),f'Unsafe/missing product image for {pid}')
        values=[price(v.get('G')) for v in variations]
        guard(all(v is not None and v>0 for v in values),f'Invalid price for {pid}')
        stocks=[]
        for v in variations:
            count=price(v.get('I'))
            guard(count is not None and count>=0 and count.is_integer(),f'Invalid stock for {pid}')
            stocks.append(int(count))
        opts=[]
        for r,cnt,val in zip(variations,stocks,values):
            n=r.get('D','').strip()
            if n:opts.append({'name':n,'price':val,'stock':cnt})
        option_images={}
        for c1,c2 in zip(('Q','S','U','W','Y','AA','AC','AE','AG'),('R','T','V','X','Z','AB','AD','AF','AH')):
            k=m.get(c1,'').strip();v=m.get(c2,'').strip()
            if k and v and urlok(v):option_images[k]=v
        product={
          'id':pid,'title':name,'rawTitle':b.get('C',''),
          'description':b.get('D','').strip(),'category':category(m.get('D',''),name),
          'categoryRaw':m.get('D',''),'priceMin':min(values),'priceMax':max(values),
          'stock':sum(stocks),'images':photos,'cover':cover,
          'url':f'https://shopee.ph/product/80730266/{pid}',
          'variants':opts,'sourceUpdatedAt':now
        }
        if m.get('O','') and urlok(m['O']):product['sizeChart']=m['O']
        if option_images:product['optionImages']=option_images
        products.append(product)
    guard(len(products)==len(basic),'Product import mismatch')
    guard(all(p['url'].rsplit('/',1)[-1]==p['id'] for p in products),'Product link identity mismatch')
    buckets=[products[i:i+40] for i in range(0,len(products),40)]
    guard(len(buckets)==8,f'Expected 8 catalog chunks; got {len(buckets)}')
    for i,bucket in enumerate(buckets,1):
        dest=OUT/f'products-{i}.json'
        tmp=OUT/f'.products-{i}.json.tmp'
        tmp.write_text(json.dumps(bucket,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        tmp.replace(dest)
    newids={p['id'] for p in products}
    info={
      'date':now,'sources':{'basic':os.path.basename(basic_file),'sales':os.path.basename(sales_file),'media':os.path.basename(media_file)},
      'totalProducts':len(products),'totalVariants':len(sales),
      'added':len(newids-oldids),'removed':len(oldids-newids),
      'addedIDs':sorted(newids-oldids),'noLongerInExportIDs':sorted(oldids-newids),
      'catalogStockZeroCount':sum(p['stock']==0 for p in products),
      'categories':dict(collections.Counter(p['category'] for p in products))
    }
    (OUT/'catalog-sync-manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(info,ensure_ascii=False,indent=2))
if __name__=='__main__':
    guard(len(sys.argv)==4,'Usage: python3 script.py BASIC.xlsx SALES.xlsx MEDIA.xlsx')
    main(*sys.argv[1:])
