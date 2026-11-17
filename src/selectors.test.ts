import {describe,it,expect} from 'vitest';
import {filterOperators} from './selectors';
import type {OperatorEntry} from './types';
const entries:OperatorEntry[]=[{id:'a',name:'甲',tier:1,coreBondIds:['x'],additionalBondIds:['y'],traitType:'类型',normalTrait:'文本',eliteTrait:null,sourceUrl:''},{id:'b',name:'乙',tier:2,coreBondIds:['x'],additionalBondIds:[],traitType:'其他',normalTrait:null,eliteTrait:null,sourceUrl:''}];
describe('operator filtering',()=>{it('intersects bond, tier, trait and name filters',()=>{expect(filterOperators(entries,'x',['y'],'甲','1','类型','asc').map(o=>o.id)).toEqual(['a']);expect(filterOperators(entries,'x',['y'],'','2','','asc')).toEqual([])});it('sorts by descending tier',()=>expect(filterOperators(entries,null,[],'','','','desc').map(o=>o.id)).toEqual(['b','a']))});
