#!/usr/bin/env python3
"""Resolve and download images explicitly present in the selected PRTS revision."""
import argparse, hashlib, json, mimetypes, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
HEADERS={'User-Agent':'SweepLookup/1.0 (local static research; contact site maintainer)'}

def read_url(url, retries=3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=20) as response:
                data=response.read(8*1024*1024+1)
                if len(data)>8*1024*1024: raise ValueError('Response exceeds 8 MB')
                return data
        except Exception:
            if attempt==retries-1: raise
            time.sleep(2**attempt)

def extract(html,bonds,operators,revision):
    found=re.search(r'"wgRevisionId"\s*:\s*(\d+)',html)
    if not found or int(found.group(1))!=revision: raise ValueError('HTML revision does not match the local data snapshot')
    soup=BeautifulSoup(html,'html.parser'); mapping={}; errors=[]
    for b in bonds:
        candidates=set()
        for label in soup.find_all('b',string=b['name']):
            table=label.find_parent('table'); row=label.find_parent('tr')
            if not table or not row or '激活所需人数' not in row.get_text(): continue
            img=row.find('img',src=True)
            if img: candidates.add(img['src'])
        if len(candidates)==1: mapping['bond:'+b['id']]=next(iter(candidates))
        else: errors.append({'kind':'bond','name':b['name'],'reason':f'{len(candidates)} matching image URLs'})
    for o in operators:
        candidates=set()
        for link in soup.find_all('a',title=o['name']):
            for img in link.find_all('img',id='charicon',src=True):
                if img['src']: candidates.add(img['src'])
        if len(candidates)==1: mapping['operator:'+o['id']]=next(iter(candidates))
        else: errors.append({'kind':'operator','name':o['name'],'tier':o['tier'],'reason':f'{len(candidates)} matching image URLs'})
    return mapping,errors

def extension(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return '.png'
    if data.startswith(b'\xff\xd8\xff'): return '.jpg'
    if data.startswith(b'RIFF') and data[8:12]==b'WEBP': return '.webp'
    if data.startswith((b'GIF87a',b'GIF89a')): return '.gif'
    raise ValueError('Unsupported or invalid image content')

def save_json(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); tmp.replace(path)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--html',help='Use previously saved source HTML (must match the data revision)'); ap.add_argument('--delay',type=float,default=0.3);args=ap.parse_args()
    directory=ROOT/'public/data'; bonds=json.loads((directory/'bonds.json').read_text()); operators=json.loads((directory/'operators.json').read_text()); meta=json.loads((directory/'metadata.json').read_text())
    page=meta['sourcePages'][0]; revision=page['revisionId']
    if not isinstance(revision,int): raise ValueError('Data revision is not available')
    url=page['url']+'?oldid='+str(revision)
    html=Path(args.html).read_text() if args.html else read_url(url).decode('utf-8')
    mapping,errors=extract(html,bonds,operators,revision)
    previous_path=ROOT/'data/reports/images.json'
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else {}
    cached=previous.get('files',{}); files={}; resolved={}; downloads={}
    for key,record in cached.items():
        path=record.get('path')
        if path and (ROOT/'public'/path).is_file() and hashlib.sha256((ROOT/'public'/path).read_bytes()).hexdigest()==record.get('sha256'):
            files[key]=record
    for key,image_url in mapping.items():
        parsed=urllib.parse.urlparse(image_url)
        if parsed.scheme!='https' or parsed.hostname!='media.prts.wiki': errors.append({'key':key,'reason':'untrusted image host'}); continue
        if image_url in downloads: resolved[key]=downloads[image_url]; continue
        old=cached.get(key,{})
        if old.get('url')==image_url and old.get('path') and (ROOT/'public'/old['path']).is_file():
            path=old['path']; digest=hashlib.sha256((ROOT/'public'/path).read_bytes()).hexdigest()
            if digest==old.get('sha256'): resolved[key]=downloads[image_url]=(path,digest); continue
        try:
            content=read_url(image_url); ext=extension(content); digest=hashlib.sha256(content).hexdigest(); folder='icons' if key.startswith('bond:') else 'avatars'; path=f'{folder}/{digest[:24]}{ext}'
            destination=ROOT/'public'/path; destination.parent.mkdir(parents=True,exist_ok=True); tmp=destination.with_suffix(destination.suffix+'.tmp'); tmp.write_bytes(content); tmp.replace(destination)
            resolved[key]=downloads[image_url]=(path,digest); print(f'{key}: {path}',flush=True)
        except Exception as e: errors.append({'key':key,'url':image_url,'reason':str(e)}); print(f'{key}: {e}',file=sys.stderr,flush=True)
        time.sleep(max(0.3,args.delay))
    for key,(path,digest) in resolved.items(): files[key]={'path':path,'url':mapping[key],'sha256':digest}
    for b in bonds:
        key='bond:'+b['id']
        if key in resolved: b['iconPath']=resolved[key][0]
    for o in operators:
        key='operator:'+o['id']
        if key in resolved: o['avatarPath']=resolved[key][0]
    meta['counts']['missingAvatars']=sum(not o.get('avatarPath') or not (ROOT/'public'/o['avatarPath']).is_file() for o in operators)
    for n,obj in [('bonds',bonds),('operators',operators),('metadata',meta)]: save_json(directory/(n+'.json'),obj)
    report={'revisionId':revision,'pageUrl':page['url'],'files':files,'errors':errors,'counts':{'icons':sum(bool(b.get('iconPath')) and (ROOT/'public'/b['iconPath']).is_file() for b in bonds),'operatorsWithAvatars':len(operators)-meta['counts']['missingAvatars'],'missingAvatars':meta['counts']['missingAvatars']}}
    save_json(previous_path,report)
    sync_path=ROOT/'data/reports/sync.json'
    if sync_path.exists():
        sync=json.loads(sync_path.read_text()); sync['counts']=meta['counts']; sync['missingAvatars']=[o['name']+' '+str(o['tier']) for o in operators if not o.get('avatarPath')]; save_json(sync_path,sync)
    print(json.dumps(report['counts'],ensure_ascii=False))
if __name__=='__main__':
    try: main()
    except Exception as e: print('Image sync failed; existing data preserved:',e,file=sys.stderr);sys.exit(1)
