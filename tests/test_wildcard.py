"""Test f2s.fnmatch."""

from __future__ import unicode_literals

import unittest

from fs import wildcard


class TestFNMatch(unittest.TestCase):
    """Test wildcard."""

    def test_wildcard(self):
        self.assertTrue(wildcard.match("*.py", "file.py"))
        self.assertTrue(wildcard.match("????.py", "????.py"))
        self.assertTrue(wildcard.match("file.py", "file.py"))
        self.assertTrue(wildcard.match("file.py[co]", "file.pyc"))
        self.assertTrue(wildcard.match("file.py[co]", "file.pyo"))
        self.assertTrue(wildcard.match("file.py[!c]", "file.py0"))
        self.assertTrue(wildcard.match("file.py[^]", "file.py^"))

        self.assertFalse(wildcard.match("*.jpg", "file.py"))
        self.assertFalse(wildcard.match("toolong.py", "????.py"))
        self.assertFalse(wildcard.match("file.pyc", "file.py"))
        self.assertFalse(wildcard.match("file.py[co]", "file.pyz"))
        self.assertFalse(wildcard.match("file.py[!o]", "file.pyo"))
        self.assertFalse(wildcard.match("file.py[]", "file.py0"))

        self.assertTrue(wildcard.imatch("*.py", "FILE.py"))
        self.assertTrue(wildcard.imatch("*.py", "file.PY"))

        self.assertFalse(wildcard.match("foo*.jpg", "foo/a.jpg"))
        self.assertTrue(wildcard.match("foo**.jpg", "foo/a.jpg"))
        self.assertTrue(wildcard.match("foo**", "foo/a.jpg"))
        self.assertTrue(wildcard.match("**.jpg", "foo/a.jpg"))
        self.assertTrue(wildcard.match("**", "foo/a.jpg"))

    def test_wildcard_accept_prefix(self):
        self.assertTrue(wildcard.match("*.py", "file", accept_prefix=True))
        self.assertTrue(wildcard.match("????.py", "????", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py", "file.p", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py[co]", "file.p", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py[co]", "file.p", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py[!c]", "file.py", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py[^]", "file.py^", accept_prefix=True))

        self.assertTrue(wildcard.match("*.jpg", "file.py", accept_prefix=True))
        self.assertFalse(wildcard.match("toolong.py", "????.py", accept_prefix=True))
        self.assertFalse(wildcard.match("file.pyc", "file.pyca", accept_prefix=True))
        self.assertFalse(wildcard.match("file.py[co]", "file.pyx", accept_prefix=True))
        self.assertFalse(wildcard.match("file.py[!o]", "file.pyo", accept_prefix=True))
        self.assertTrue(wildcard.match("file.py[]", "f", accept_prefix=True))

        self.assertTrue(wildcard.imatch("*.py", "FILE.p", accept_prefix=True))
        self.assertTrue(wildcard.imatch("*.py", "file.", accept_prefix=True))

        self.assertFalse(wildcard.match("foo*.jpg", "foo/", accept_prefix=True))
        self.assertTrue(wildcard.match("foo**.jpg", "foo", accept_prefix=True))
        self.assertTrue(wildcard.match("foo**", "foo/", accept_prefix=True))
        self.assertTrue(wildcard.match("**.jpg", "foo", accept_prefix=True))
        self.assertTrue(wildcard.match("**", "foo/a.j", accept_prefix=True))

    def test_match_any(self):
        self.assertTrue(wildcard.match_any([], "foo.py"))
        self.assertTrue(wildcard.imatch_any([], "foo.py"))
        self.assertTrue(wildcard.match_any(["*.py", "*.pyc"], "foo.pyc"))
        self.assertTrue(wildcard.imatch_any(["*.py", "*.pyc"], "FOO.pyc"))

    def test_get_matcher(self):
        matcher = wildcard.get_matcher([], True)
        self.assertTrue(matcher("foo.py"))
        matcher = wildcard.get_matcher(["*.py"], True)
        self.assertTrue(matcher("foo.py"))
        self.assertFalse(matcher("foo.PY"))
        matcher = wildcard.get_matcher(["*.py"], False)
        self.assertTrue(matcher("foo.py"))
        self.assertTrue(matcher("FOO.py"))
