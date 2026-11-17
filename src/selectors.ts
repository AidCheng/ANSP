import type {OperatorEntry} from './types';
export function filterOperators(operators:OperatorEntry[], current:string|null, selected:string[], query:string, tier:string, trait:string, sort:string) {
 const ids = [...new Set([...(current ? [current] : []), ...selected])];
 return operators.filter(o => ids.every(id => [...o.coreBondIds,...o.additionalBondIds].includes(id)) && o.name.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()) && (!tier || o.tier === Number(tier)) && (!trait || o.traitType === trait)).sort((a,b) => sort === 'name' ? a.name.localeCompare(b.name,'zh-CN') || a.tier-b.tier : (sort === 'desc' ? b.tier-a.tier : a.tier-b.tier) || a.name.localeCompare(b.name,'zh-CN'));
}
export const assetUrl = (path:string) => `${import.meta.env.BASE_URL}${path.replace(/^\/+/, '')}`;

/** Extract only source-stated timing markers, ignoring struck-through text. */
export function traitTiming(normal:string|null, elite:string|null):string {
 const text=[normal,elite].filter(Boolean).join('\n').replace(/<del\b[^>]*>[\s\S]*?<\/del>/gi,'');
 const timings=Array.from(text.matchAll(/<(获得时|售出时|战斗中|进入休整期时|休整期结束时|战斗开始时|战斗结束时|刷新时|开启技能时|休整期开始时)>/g), match=>match[1]);
 return [...new Set(timings)].join(' / ') || '时机未标明';
}
