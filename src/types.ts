export type BondCategory = 'core' | 'additional';
export interface Bond { id:string; name:string; category:BondCategory; activationCount:number|null; effectText:string; extraEffectText?:string|null; notes?:string[]; sourceUrl:string }
export interface OperatorEntry { id:string; name:string; tier:1|2|3|4|5|6; prototypeName?:string|null; avatarPath?:string|null; coreBondIds:string[]; additionalBondIds:string[]; traitType:string|null; normalTrait:string|null; eliteTrait:string|null; sourceUrl:string }
export interface Metadata { displayName:string; fetchedAt:string|null; status?:string; sourcePages:{url:string;revisionId:number|null}[]; counts:{bonds:number;operators:number;missingAvatars:number} }
