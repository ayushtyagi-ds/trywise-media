import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import render_carousel,review_server
class EvidenceTest(unittest.TestCase):
 def test_evidence_rendered_escaped_and_part_of_approval(self):
  source={'title':'Example','url':'https://example.com/story','published_at':'2026-10-30'}
  draft={'source':source,'slides':[{'heading':'Heading','body':'Body'}]*3,'caption':'Caption','claims':[{'text':'<script>bad</script>','evidence':'An excerpt'}],'review_notes':['Check context']}
  with tempfile.TemporaryDirectory() as tmp:
   dest=Path(tmp)/'carousel';render_carousel.render(draft,dest);snap=review_server.snapshot(dest);page=review_server.page(snap,'token')
   self.assertIn(b'An excerpt',page);self.assertIn(b'Check context',page);self.assertIn(b'&lt;script&gt;',page);self.assertNotIn(b'<script>bad</script>',page)
   review_server.write_approval(dest,snap['digest']);before=snap['digest'];manifest=dest/'manifest.json';manifest.write_text(manifest.read_text().replace('Check context','Check more context'));self.assertNotEqual(before,review_server.snapshot(dest)['digest'])
