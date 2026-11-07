import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import buffer_adapter as b

class BufferTest(unittest.TestCase):
    def setUp(self):
        self.manifest = {'channel_id':'test', 'caption':'Hello!', 'image_urls':['https://example.com/1.png','https://example.com/2.png']}

    def test_preview_order_and_no_network(self):
        with patch('urllib.request.build_opener', side_effect=AssertionError('unexpected network')):
            preview = b.payload_for_preview(self.manifest)
        self.assertEqual([x['image']['url'] for x in preview['variables']['input']['assets']], self.manifest['image_urls'])
        self.assertEqual(preview['variables']['input']['schedulingType'], 'automatic')
        self.assertIs(preview['variables']['input']['needsApproval'], False)
        self.assertEqual(preview['variables']['input']['metadata']['instagram'], {'type':'post','shouldShareToFeed':True})

    def test_rejects_credentials_and_secrets_in_image_urls(self):
        for url in ['http://example.com/x.png', 'https://x:y@example.com/x', 'https://example.com/a?token=secret', 'https://example.com/a#x']:
            with self.subTest(url=url):
                with self.assertRaises(ValueError): b.validate_manifest({**self.manifest, 'image_urls':[url]})

    def test_digest_binds_content_and_destination(self):
        digest = b.manifest_digest(self.manifest)
        self.assertNotEqual(digest, b.manifest_digest({**self.manifest, 'caption':'changed'}))
        self.assertNotEqual(digest, b.manifest_digest({**self.manifest, 'channel_id':'other'}))
        self.assertNotEqual(digest, b.manifest_digest({**self.manifest, 'image_urls':list(reversed(self.manifest['image_urls']))}))

    def test_disallows_arbitrary_query(self):
        with self.assertRaises(ValueError): b.read_only_query('mutation { createPost }')

    def test_organizations_is_a_readonly_query(self):
        from io import BytesIO
        class FakeResponse(BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()
        class FakeOpener:
            def open(self, request, timeout):
                self.request = request
                return FakeResponse(b'{"data":{"account":{"organizations":[{"id":"123","name":"test"}]}}}')
        fake = FakeOpener()
        with patch.dict(os.environ, {'BUFFER_API_KEY':'secret-token'}), patch('urllib.request.build_opener', return_value=fake):
            response = b.read_only_query(b.ACCOUNT_QUERY)
        self.assertEqual(response['account']['organizations'][0]['id'], '123')
        request_body = json.loads(fake.request.data)
        self.assertEqual(request_body['query'], b.ACCOUNT_QUERY)
        self.assertNotIn('mutation', request_body['query'])
        self.assertNotIn('secret-token', json.dumps(response))

    def test_missing_key_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError): b.read_only_query(b.ACCOUNT_QUERY)

    def test_readonly_request_never_returns_key_on_error(self):
        import urllib.error
        with patch.dict(os.environ, {'BUFFER_API_KEY':'secret-token'}), patch('urllib.request.build_opener', side_effect=urllib.error.URLError('secret-token')):
            with self.assertRaises(RuntimeError) as error: b.read_only_query(b.ACCOUNT_QUERY)
        self.assertNotIn('secret-token', str(error.exception))

if __name__ == '__main__': unittest.main()
