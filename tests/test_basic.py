import os
import tempfile
import unittest

from jobwatch.core import _format, _match
from jobwatch.state import State
from jobwatch.sources import parse_rss


class TestMatch(unittest.TestCase):
    def test_no_keywords(self):
        self.assertTrue(_match({"title": "Python Dev", "company": "X", "tags": []}, []))

    def test_keyword_in_title(self):
        self.assertTrue(_match({"title": "Senior Python Dev", "company": "X", "tags": []}, ["python"]))

    def test_keyword_in_tags(self):
        self.assertTrue(_match({"title": "Dev", "company": "X", "tags": ["python", "remote"]}, ["python"]))

    def test_no_match(self):
        self.assertFalse(_match({"title": "Designer", "company": "X", "tags": []}, ["python"]))


class TestFormat(unittest.TestCase):
    def test_format(self):
        j = {
            "title": "Dev",
            "company": "ACME",
            "location": "Remote",
            "salary": "$50k",
            "url": "https://x",
        }
        line = _format(j)
        self.assertIn("Dev", line)
        self.assertIn("ACME", line)
        self.assertIn("https://x", line)


class TestState(unittest.TestCase):
    def test_new_and_seen(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.json")
            st = State(path)
            jobs = [{"id": "1"}, {"id": "2"}]
            self.assertEqual(st.new_jobs(jobs), jobs)
            st.mark_seen(jobs)
            st.save()
            st2 = State(path)
            self.assertEqual(st2.new_jobs(jobs), [])
            self.assertEqual(st2.new_jobs([{"id": "3"}]), [{"id": "3"}])


class TestRss(unittest.TestCase):
    def test_parse_rss(self):
        rss = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<item><title>Python Dev</title><link>https://x/1</link><guid>123</guid><pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate></item>
<item><title>Data Analyst</title><link>https://x/2</link><guid>124</guid></item>
</channel></rss>"""
        jobs = parse_rss(rss)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "Python Dev")
        self.assertEqual(jobs[0]["id"], "123")
        self.assertEqual(jobs[1]["url"], "https://x/2")

    def test_parse_atom(self):
        atom = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>jobs</title>
<entry>
  <title>Python Dev</title>
  <link rel="alternate" type="text/html" href="https://x/t/1#reply2" />
  <id>tag:example.com:/t/1</id>
  <updated>2026-09-10T12:00:00Z</updated>
</entry>
</feed>"""
        jobs = parse_rss(atom)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Python Dev")
        self.assertEqual(jobs[0]["id"], "tag:example.com:/t/1")
        self.assertEqual(jobs[0]["url"], "https://x/t/1#reply2")


if __name__ == "__main__":
    unittest.main()
