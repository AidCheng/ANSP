import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sync_prts import fields, clean, parse
from validate_data import validate
class ParserTests(unittest.TestCase):
    def test_nested_and_multiline(self):
        f=fields('x|干员=甲|特质1=<获得时>{{color|red|+2}}<br>第二行|原型=乙')
        self.assertEqual(f['原型'],'乙'); self.assertEqual(clean(f['特质1']),'<获得时>+2\n第二行')
    def test_reject_unknown_bond(self):
        text='=== 核心盟约 ===\n{{卫戍协议/盟约|盟约=甲|人数=1|效果=效果}}\n{{color|x|Ⅰ}}阶干员\n{{卫戍协议/参战干员|干员=乙|盟约1=不存在}}'
        with self.assertRaisesRegex(ValueError,'Unresolved'): parse(text,{'wikiBaseUrl':'https://example.com','wikiPageTitle':'a','datasetId':'x'},1)
    def test_real_page_fixture(self):
        text=(Path(__file__).resolve().parents[2]/'data/fixtures/prts-minimal.wikitext').read_text()
        bonds, operators, _ = parse(text, {'wikiBaseUrl':'https://prts.wiki','wikiPageTitle':'卫戍协议：盟约/PRTS盟约记录','datasetId':'fixture','displayName':'fixture'}, 449018)
        self.assertEqual(operators[0]['name'], '讯使')
        self.assertEqual(operators[0]['tier'], 1)
        self.assertEqual(len(operators[0]['additionalBondIds']), 1)
        self.assertIn('获得时', operators[0]['normalTrait'])
    def test_empty_snapshot_is_invalid(self): self.assertTrue(validate([],[],{'counts':{'bonds':0,'operators':0}}))
if __name__=='__main__': unittest.main()
