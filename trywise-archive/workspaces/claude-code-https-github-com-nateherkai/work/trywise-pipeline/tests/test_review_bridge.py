import hashlib, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import buffer_adapter, review_bridge as b, review_server as review

PNG = b'\x89PNG\r\n\x1a\n' + b'example slide bytes'
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)
  (self.path/'01.png').write_bytes(PNG)
  (self.path/'caption.txt').write_text('Example caption')
  (self.path/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{'title':'Example'}}))
  review.write_approval(self.path,review.snapshot(self.path)['digest'])
  self.url='https://cdn.example.com/one.png'
 def tearDown(self): self.temp.cleanup()
 def test_matches_bytes_and_binds_caption_channel_and_url(self):
  out=b.create_manifest(self.path,'channel',[self.url],{'cdn.example.com'},lambda u,h:PNG)
  self.assertEqual(out['caption'],'Example caption')
  self.assertEqual(out['_review_verification']['buffer_manifest_digest'],buffer_adapter.manifest_digest(out))
  self.assertEqual(out['_review_verification']['hosted_slides'][0]['sha256'],hashlib.sha256(PNG).hexdigest())
 def test_rejects_changed_local_content(self):
  (self.path/'caption.txt').write_text('Changed')
  with self.assertRaises(ValueError):b.create_manifest(self.path,'channel',[self.url],{'cdn.example.com'},lambda u,h:PNG)
 def test_rejects_changed_remote_bytes(self):
  with self.assertRaises(ValueError):b.create_manifest(self.path,'channel',[self.url],{'cdn.example.com'},lambda u,h:PNG+b'changed')
 def test_rejects_wrong_slide_count(self):
  with self.assertRaises(ValueError):b.create_manifest(self.path,'channel',[],{'cdn.example.com'},lambda u,h:PNG)
 def test_rejects_non_allowed_and_non_public_urls(self):
  for url in ['http://cdn.example.com/a','https://elsewhere.example.com/a','https://cdn.example.com/a?token=abc','https://127.0.0.1/a','https://cdn.example.com:8443/a','https://cdn.example.com@evil.com/a']:
   with self.subTest(url=url):
    with self.assertRaises(ValueError):b.checked_url(url,{'cdn.example.com','127.0.0.1'})
 def test_private_and_mapped_addresses_blocked(self):
  for ip in ['127.0.0.1','169.254.169.254','10.0.0.3','::1','::ffff:127.0.0.1','224.0.0.1']:
   self.assertFalse(b.public_ip(ip),ip)
  self.assertTrue(b.public_ip('8.8.8.8'))
 def test_refuses_private_dns_before_network_connection(self):
  with patch.object(b.socket,'getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]), patch.object(b.http.client,'HTTPSConnection') as con:
   with self.assertRaises(ValueError):b.fetch_public_png(self.url,{'cdn.example.com'})
   con.assert_not_called()
 def test_catches_local_change_during_remote_fetch(self):
  def edit(u,h):
   (self.path/'caption.txt').write_text('Mutated during fetch')
   return PNG
  with self.assertRaises(ValueError):b.create_manifest(self.path,'channel',[self.url],{'cdn.example.com'},edit)
if __name__=='__main__':unittest.main()
