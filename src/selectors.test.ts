import {describe,it,expect} from 'vitest';
import {filterOperators} from './selectors';
import type {OperatorEntry} from './types';
const entries:OperatorEntry[]=[{id:'a',name:'甲',tier:1,coreBondIds:['x'],additionalBondIds:['y'],traitType:'类型',normalTrait:'文本',eliteTrait:null,sourceUrl:''},{id:'b',name:'乙',tier:2,coreBondIds:['x'],additionalBondIds:[],traitType:'其他',normalTrait:null,eliteTrait:null,sourceUrl:''}];
describe('operator filtering',()=>{it('intersects bond, tier, trait and name filters',()=>{expect(filterOperators(entries,'x',['y'],'甲','1','类型','asc').map(o=>o.id)).toEqual(['a']);expect(filterOperators(entries,'x',['y'],'','2','','asc')).toEqual([])});it('sorts by descending tier',()=>expect(filterOperators(entries,null,[],'','','','desc').map(o=>o.id)).toEqual(['b','a']))});

import {traitTiming} from './selectors';
describe('trait timing',()=>{
 it('shows explicit timing and removes struck-through text',()=>{
  expect(traitTiming('<del><获得时>旧效果</del>\n<战斗中>新效果',null)).toBe('战斗中');
  expect(traitTiming('<获得时>效果','<获得时>效果')).toBe('获得时');
  expect(traitTiming('没有时机标记',null)).toBe('时机未标明');
 });
});
