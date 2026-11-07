import sqlite3
import datetime as dt
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import trywise

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.db = trywise.connect(':memory:')
        self.data = (Path(__file__).parent / 'sample.xml').read_bytes()
    def tearDown(self): self.db.close()
    def test_dedupe_and_idempotency(self):
        self.assertEqual(trywise.ingest(self.db, self.data, 'https://example.com/rss'), 2)
        self.assertEqual(trywise.ingest(self.db, self.data, 'https://example.com/rss'), 0)
        self.assertEqual(self.db.execute('select count(*) from stories').fetchone()[0],2)
    def test_no_partial_writes_on_malformed_xml(self):
        with self.assertRaises(ET.ParseError): trywise.ingest(self.db, b'<rss><item>', 'https://example.com/rss')
        self.assertEqual(self.db.execute('select count(*) from stories').fetchone()[0],0)
    def test_fresh_filter_skips_stale_and_undated(self):
        cutoff = dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)
        self.assertEqual(trywise.ingest(self.db, self.data, 'https://example.com/rss', cutoff), 1)
        self.assertEqual(self.db.execute('select title from stories').fetchone()[0], 'Example announcement')
        self.assertEqual(trywise.ingest(self.db, self.data, 'https://example.com/rss', cutoff), 0)
    def test_atom_and_relative_url(self):
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Demo</title><link href="/story"/><updated>2026-10-30T12:00:00Z</updated></entry></feed>'
        story = list(trywise.parse_feed(atom, 'https://example.com/rss'))[0]
        self.assertEqual(story['url'], 'https://example.com/story')
        self.assertEqual(story['published_at'], '2026-10-30T12:00:00+00:00')
    def test_unsafe_xml_rejected(self):
        with self.assertRaises(ValueError): list(trywise.parse_feed(b'<!DOCTYPE rss><rss/>','https://example.com'))
    def test_invalid_urls_skipped(self):
        rss=b'<rss><channel><item><title>bad</title><link>javascript:evil</link></item></channel></rss>'
        self.assertEqual(list(trywise.parse_feed(rss,'https://example.com')),[])

if __name__ == '__main__': unittest.main()
