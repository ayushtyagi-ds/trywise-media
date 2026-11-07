import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import source_capture as s
class CaptureTests(unittest.TestCase):
 def test_text_excludes_scripts(self):
  self.assertEqual(s.extract(b'<h1>Headline</h1><script>bad</script><p>Hello <b>world</b></p>'),'Headline\nHello world')
 def test_only_allowlisted_https(self):
  for url in ('http://example.com/','https://evil.com/','https://example.com@evil.com/','https://example.com:444/'):
   with self.assertRaises(ValueError): s.validate_url(url,{'example.com'})
  self.assertEqual(s.validate_url('https://example.com/story',{'example.com'}),'https://example.com/story')
if __name__=='__main__': unittest.main()
