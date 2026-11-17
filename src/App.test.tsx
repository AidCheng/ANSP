// @vitest-environment jsdom
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import App from './App';
const bonds=[{id:'x',name:'核心甲',category:'core',activationCount:3,effectText:'真实效果测试',sourceUrl:''},{id:'y',name:'附加乙',category:'additional',activationCount:2,effectText:'附加效果测试',sourceUrl:''}];
const operators=[{id:'a',name:'测试甲',tier:1,avatarPath:null,coreBondIds:['x'],additionalBondIds:['y'],traitType:'作战能力',normalTrait:'普通文本',eliteTrait:null,sourceUrl:''},{id:'b',name:'测试乙',tier:2,avatarPath:null,coreBondIds:['x'],additionalBondIds:[],traitType:'整备能力',normalTrait:'其他文本',eliteTrait:'精锐文本',sourceUrl:''}];
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn(async (url:string)=>({ok:true,json:async()=>url.includes('bonds')?bonds:url.includes('operators')?operators:{displayName:'测试',fetchedAt:null,sourcePages:[],counts:{bonds:2,operators:2,missingAvatars:2}}}))) });
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
describe('explorer',()=>{it('selects bonds and operators and applies intersection and filters',async()=>{render(<App/>);await screen.findByText('真实效果测试');expect(screen.getByText('测试甲')).toBeTruthy();fireEvent.click(screen.getByText('测试甲'));expect(screen.getByText('普通文本')).toBeTruthy();expect(screen.getByText('未收录')).toBeTruthy();fireEvent.click(screen.getByLabelText('添加 附加乙 筛选'));expect(screen.queryByText('测试乙')).toBeNull();fireEvent.change(screen.getByLabelText('搜索干员名称'),{target:{value:'不存在'}});expect(screen.getByText('没有符合条件的干员')).toBeTruthy();fireEvent.click(screen.getAllByText('清空筛选')[0]);fireEvent.click(screen.getByRole('button',{name:'◇附加乙附加盟约'}));await waitFor(()=>expect(screen.getByText('附加效果测试')).toBeTruthy())})});
