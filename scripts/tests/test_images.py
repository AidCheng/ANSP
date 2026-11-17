import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sync_images import extract, extension
class ImageTests(unittest.TestCase):
    def test_extract_verified_links(self):
        html='''<script>{"wgRevisionId":12}</script><table><tr><td><img src="https://media.prts.wiki/icon.png"><b>炎</b>激活所需人数</td></tr></table><a title="讯使"><img id="charicon" src="https://media.prts.wiki/portrait.png"></a>'''
        bonds=[{'id':'x','name':'炎'}]; operators=[{'id':'y','name':'讯使','tier':1}]
        mapping,errors=extract(html,bonds,operators,12)
        self.assertEqual(mapping['bond:x'],'https://media.prts.wiki/icon.png');self.assertEqual(mapping['operator:y'],'https://media.prts.wiki/portrait.png');self.assertEqual(errors,[])
        with self.assertRaises(ValueError): extract(html,bonds,operators,13)
    def test_ambiguous_image_is_not_guessed(self):
        html='''<script>{"wgRevisionId":12}</script><a title="讯使"><img id="charicon" src="a"></a><a title="讯使"><img id="charicon" src="b"></a>'''
        mapping,errors=extract(html,[],[{'id':'y','name':'讯使','tier':1}],12)
        self.assertNotIn('operator:y',mapping);self.assertEqual(len(errors),1)
    def test_image_validation(self):
        self.assertEqual(extension(b'\x89PNG\r\n\x1a\nrest'),'.png')
        with self.assertRaises(ValueError): extension(b'<html>error</html>')
if __name__=='__main__': unittest.main()
