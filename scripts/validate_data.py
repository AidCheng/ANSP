#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def validate(bonds,operators,meta):
    errors=[]; ids={}; seen=set()
    for b in bonds:
        if not b.get('id') or b['id'] in ids: errors.append('duplicate/missing bond id')
        ids[b.get('id')]=b.get('category')
        if b.get('category') not in ('core','additional') or not b.get('name') or not b.get('effectText'): errors.append('invalid bond')
    for o in operators:
        if not o.get('id') or o['id'] in seen: errors.append('duplicate/missing operator id')
        seen.add(o.get('id'))
        if o.get('tier') not in range(1,7): errors.append('invalid tier')
        for field,cat in [('coreBondIds','core'),('additionalBondIds','additional')]:
            for bid in o.get(field,[]):
                if ids.get(bid)!=cat: errors.append('invalid bond reference: '+str(bid))
    if not bonds or not operators: errors.append('snapshot is empty')
    if meta.get('counts',{}).get('bonds')!=len(bonds) or meta.get('counts',{}).get('operators')!=len(operators): errors.append('metadata count mismatch')
    return errors
if __name__=='__main__':
    try:
        data=[json.loads((ROOT/'public/data'/f'{x}.json').read_text()) for x in ('bonds','operators','metadata')]; errors=validate(*data)
        if errors: print('\n'.join(errors)); sys.exit(1)
        print(f"Validated {len(data[0])} bonds and {len(data[1])} operators.")
    except Exception as e: print(e); sys.exit(1)
