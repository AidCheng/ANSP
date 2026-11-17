import type {OperatorEntry} from './types';
export function filterOperators(operators:OperatorEntry[], current:string|null, selected:string[], query:string, tier:string, trait:string, sort:string) {
 const ids = [...new Set([...(current ? [current] : []), ...selected])];
 return operators.filter(o => ids.every(id => [...o.coreBondIds,...o.additionalBondIds].includes(id)) && o.name.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()) && (!tier || o.tier === Number(tier)) && (!trait || o.traitType === trait)).sort((a,b) => sort === 'name' ? a.name.localeCompare(b.name,'zh-CN') || a.tier-b.tier : (sort === 'desc' ? b.tier-a.tier : a.tier-b.tier) || a.name.localeCompare(b.name,'zh-CN'));
}
export const assetUrl = (path:string) => `${import.meta.env.BASE_URL}${path.replace(/^\/+/, '')}`;
