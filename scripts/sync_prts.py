#!/usr/bin/env python3
"""Download one configured MediaWiki revision and atomically replace a validated snapshot."""
import argparse, datetime, hashlib, json, re, sys, tempfile, time, urllib.parse, urllib.request
from pathlib import Path
from validate_data import validate
ROOT = Path(__file__).resolve().parent.parent

def templates(text, name):
    prefix = '{{' + name + '|'; start = 0
    while True:
        i = text.find(prefix, start)
        if i < 0: return
        depth = 1; j = i + 2
        while j < len(text) and depth:
            if text[j:j+2] == '{{': depth += 1; j += 2
            elif text[j:j+2] == '}}': depth -= 1; j += 2
            else: j += 1
        if depth: raise ValueError('Unclosed template at %d' % i)
        yield i, text[i+2:j-2]
        start = j

def split_top(s):
    out=[]; start=0; depth=0; link=0; i=0
    while i < len(s):
        pair=s[i:i+2]
        if pair=='{{': depth+=1; i+=2; continue
        if pair=='}}': depth-=1; i+=2; continue
        if pair=='[[': link+=1; i+=2; continue
        if pair==']]': link-=1; i+=2; continue
        if s[i]=='|' and not depth and not link: out.append(s[start:i]); start=i+1
        i+=1
    out.append(s[start:]); return out

def fields(s):
    result={}
    for item in split_top(s)[1:]:
        if '=' in item:
            k,v=item.split('=',1); result[k.strip()]=v.strip()
    return result

def clean(s):
    s=re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s=re.sub(r'<\s*(?:br\s*/?|hr\s*/?)\s*>', '\n', s, flags=re.I)
    # Render known presentation templates; retain unknown templates verbatim.
    pattern=re.compile(r'\{\{(color|术语|修正)\|([^{}]*)\}\}')
    while pattern.search(s):
        def replace(m):
            parts=split_top(m.group(2)); return parts[-1] if m.group(1) in ('color','术语') else parts[0]
        s=pattern.sub(replace,s)
    s=re.sub(r'\[\[([^\[\]]+)\]\]',lambda m:m.group(1).split('|')[-1],s)
    return s.replace("'''",'').replace("''",'').strip()

def ident(name): return hashlib.sha256(name.encode()).hexdigest()[:16]

def parse(text, config, revision):
    url=config['wikiBaseUrl']+'/w/'+urllib.parse.quote(config['wikiPageTitle'], safe='/:')
    bonds=[]; names={}
    for pos, raw in templates(text,'卫戍协议/盟约'):
        f=fields(raw); name=f.get('盟约'); effect=f.get('效果')
        if not name or not effect: raise ValueError('Bond missing name/effect')
        core=text.rfind('=== 核心盟约 ===',0,pos); additional=text.rfind('=== 附加盟约 ===',0,pos)
        if core<0: raise ValueError('Bond category missing')
        cat='additional' if additional>core else 'core'; bid=ident(name)
        if name in names: raise ValueError('Duplicate bond '+name)
        names[name]=(bid,cat); bonds.append({'id':bid,'name':name,'category':cat,'activationCount':int(f['人数']) if f.get('人数','').isdigit() else None,'effectText':clean(effect),'sourceUrl':url})
    operators=[]; seen=set(); roman='ⅠⅡⅢⅣⅤⅥ'
    headings=list(re.finditer(r'\{\{color\|[^|{}]+\|([ⅠⅡⅢⅣⅤⅥ])\}\}阶干员',text))
    unresolved=[]
    for pos,raw in templates(text,'卫戍协议/参战干员'):
        f=fields(raw); previous=[h for h in headings if h.start()<pos]
        if not previous or not f.get('干员'): raise ValueError('Operator missing name or tier')
        tier=roman.index(previous[-1].group(1))+1; name=f['干员']; oid=ident(config['datasetId']+'|'+str(tier)+'|'+name+'|'+f.get('原型',''))
        if oid in seen: raise ValueError('Duplicate operator '+name)
        seen.add(oid); core=[]; additional=[]
        for k in ('盟约1','盟约2','盟约3'):
            if f.get(k):
                if f[k] not in names: unresolved.append(name+': '+f[k]); continue
                bid,cat=names[f[k]]; (core if cat=='core' else additional).append(bid)
        operators.append({'id':oid,'name':name,'tier':tier,'prototypeName':f.get('原型') or None,'avatarPath':None,'coreBondIds':core,'additionalBondIds':additional,'traitType':f.get('特质类型') or None,'normalTrait':clean(f['特质1']) if f.get('特质1') else None,'eliteTrait':clean(f['特质2']) if f.get('特质2') else None,'sourceUrl':url})
    if unresolved: raise ValueError('Unresolved bonds: '+', '.join(unresolved))
    if not bonds or not operators: raise ValueError('No bonds or operators parsed')
    meta={'datasetId':config['datasetId'],'displayName':config['displayName'],'sourcePages':[{'url':url,'revisionId':revision}],'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parserVersion':'1.0','counts':{'bonds':len(bonds),'operators':len(operators),'missingAvatars':len(operators)}}
    return bonds,operators,meta

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config/data-source.json'); ap.add_argument('--response',help='Read a previously downloaded API response for reproducible parsing'); args=ap.parse_args()
    config=json.loads((ROOT/args.config).read_text()); params=urllib.parse.urlencode({'action':'query','prop':'revisions','rvprop':'ids|content','rvslots':'main','format':'json','titles':config['wikiPageTitle']})
    if args.response: data=json.loads(Path(args.response).read_text())
    else:
        req=urllib.request.Request(config['wikiBaseUrl']+'/api.php?'+params,headers={'User-Agent':'SweepLookup/1.0 (local static reference; contact site maintainer)'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req,timeout=30) as r: data=json.load(r)
                break
            except Exception:
                if attempt==2: raise
                time.sleep(2**attempt)
    page=next(iter(data['query']['pages'].values())); rev=page['revisions'][0]; text=rev['slots']['main']['*']; bonds,operators,meta=parse(text,config,rev['revid'])
    # Carry forward successfully verified local images by stable ID; a later image sync refreshes mappings.
    for filename,records,field in [('bonds',bonds,'iconPath'),('operators',operators,'avatarPath')]:
        path=ROOT/'public/data'/f'{filename}.json'
        if path.exists():
            old={x['id']:x.get(field) for x in json.loads(path.read_text())}
            for record in records:
                value=old.get(record['id'])
                if value and (ROOT/'public'/value).is_file(): record[field]=value
    meta['counts']['missingAvatars']=sum(not o.get('avatarPath') for o in operators)
    errors=validate(bonds,operators,meta)
    if errors: raise ValueError('; '.join(errors))
    target=ROOT/'public/data'; target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target) as d:
        for name,obj in [('bonds',bonds),('operators',operators),('metadata',meta)]: (Path(d)/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        for name in ('bonds','operators','metadata'): (Path(d)/(name+'.json')).replace(target/(name+'.json'))
    report={'source':meta['sourcePages'],'fetchedAt':meta['fetchedAt'],'counts':meta['counts'],'tiers':{str(i):sum(o['tier']==i for o in operators) for i in range(1,7)},'missingAvatars':[o['name']+' '+str(o['tier']) for o in operators if not o.get('avatarPath')],'missingEliteTraits':sum(not o['eliteTrait'] for o in operators),'unknownTemplates':sorted(set(re.findall(r'\{\{([^|{}]+)', '\n'.join(b['effectText'] for b in bonds)+'\n'+'\n'.join((o['normalTrait'] or '')+'\n'+(o['eliteTrait'] or '') for o in operators)))), 'unresolvedBonds':[]}
    (ROOT/'data/reports/sync.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':
    try: main()
    except Exception as e: print('Sync failed; existing snapshot preserved:',e,file=sys.stderr); sys.exit(1)
