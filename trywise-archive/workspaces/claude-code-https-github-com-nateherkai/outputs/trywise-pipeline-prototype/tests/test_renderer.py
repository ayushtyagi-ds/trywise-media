import json
import os
import tempfile
import unittest
from pathlib import Path
from render_carousel import RenderError, render

HERE = Path(__file__).resolve().parents[1]

class CarouselTests(unittest.TestCase):
    def setUp(self):
        self.draft = json.loads((HERE/'example-draft.json').read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)/'new-carousel'

    def test_images_and_manifest(self):
        render(self.draft,self.target)
        self.assertEqual(len(list(self.target.glob('*.png'))),3)
        self.assertEqual(json.loads((self.target/'manifest.json').read_text())['status'],'needs_review')
        self.assertIn(self.draft['source']['url'],(self.target/'caption.txt').read_text())

    def test_rejects_overflow_and_cleans_up(self):
        self.draft['slides'][1]['body'] = ('word ' * 120).strip()
        with self.assertRaises(RenderError): render(self.draft,self.target)
        self.assertFalse(self.target.exists())
        self.assertFalse(list(Path(self.temp.name).glob('.trywise-render-*')))

    def test_existing_output_not_overwritten(self):
        self.target.mkdir()
        (self.target/'keep').write_text('safe')
        with self.assertRaises(RenderError): render(self.draft,self.target)
        self.assertEqual((self.target/'keep').read_text(),'safe')

    def test_credential_urls_rejected(self):
        self.draft['source']['url']='https://secret@example.com/news'
        with self.assertRaises(RenderError): render(self.draft,self.target)

if __name__ == '__main__': unittest.main()
