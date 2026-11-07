import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import trywise
class PermalinkGuidTests(unittest.TestCase):
 def test_explicit_permalink_is_used_if_link_absent(self):
  rss=b'<rss><channel><item><title>AI developer release</title><guid isPermaLink="true">https://huggingface.co/blog/example</guid><pubDate>Fri, 30 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>'
  self.assertEqual(list(trywise.parse_feed(rss,'https://huggingface.co/blog/feed.xml'))[0]['url'],'https://huggingface.co/blog/example')
 def test_non_permalink_and_non_https_are_ignored(self):
  for guid in (b'<guid isPermaLink="false">https://example.com/thing</guid>',b'<guid>http://example.com/thing</guid>',b'<guid>/relative</guid>'):
   self.assertEqual(list(trywise.parse_feed(b'<rss><channel><item><title>x</title>'+guid+b'</item></channel></rss>','https://example.com/feed')),[])
