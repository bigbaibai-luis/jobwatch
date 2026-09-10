import os
import tempfile
import unittest

from jobwatch.core import _format, _match
from jobwatch.state import State


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


if __name__ == "__main__":
    unittest.main()
