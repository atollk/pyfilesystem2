"""Match wildcard filenames.

    Patterns are derived from Unix shell style:

    *       matches everything except for a path seperator
    **      matches everything
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq
"""

from __future__ import unicode_literals, print_function

import typing

from .lrucache import LRUCache

if typing.TYPE_CHECKING:
    from typing import Callable, Iterable, Text, Tuple


_PATTERN_CACHE = LRUCache(1000)  # type: LRUCache[Tuple[Text, bool, bool], PatternMatcher]


def match(pattern, name, accept_prefix=False):
    # type: (Text, Text, bool) -> bool
    """Test whether a name matches a wildcard pattern.

    Arguments:
        pattern (str): A wildcard pattern, e.g. ``"*.py"``.
        name (str): A filename.

    Returns:
        bool: `True` if the filename matches the pattern.

    """
    args = (pattern, True, accept_prefix)
    try:
        pat = _PATTERN_CACHE[args]
    except KeyError:
        pat = PatternMatcher(*args)
        _PATTERN_CACHE[args] = pat
    return pat(name)


def imatch(pattern, name, accept_prefix=False):
    # type: (Text, Text, bool) -> bool
    """Test whether a name matches a wildcard pattern (case insensitive).

    Arguments:
        pattern (str): A wildcard pattern, e.g. ``"*.py"``.
        name (bool): A filename.

    Returns:
        bool: `True` if the filename matches the pattern.

    """
    args = (pattern, False, accept_prefix)
    try:
        pat = _PATTERN_CACHE[args]
    except KeyError:
        pat = PatternMatcher(*args)
        _PATTERN_CACHE[args] = pat
    return pat(name)


def match_any(patterns, name, accept_prefix=False):
    # type: (Iterable[Text], Text, bool) -> bool
    """Test if a name matches any of a list of patterns.

    Will return `True` if ``patterns`` is an empty list.

    Arguments:
        patterns (list): A list of wildcard pattern, e.g ``["*.py",
            "*.pyc"]``
        name (str): A filename.

    Returns:
        bool: `True` if the name matches at least one of the patterns.

    """
    if not patterns:
        return True
    return any(match(pattern, name, accept_prefix) for pattern in patterns)


def imatch_any(patterns, name, accept_prefix=False):
    # type: (Iterable[Text], Text, bool) -> bool
    """Test if a name matches any of a list of patterns (case insensitive).

    Will return `True` if ``patterns`` is an empty list.

    Arguments:
        patterns (list): A list of wildcard pattern, e.g ``["*.py",
            "*.pyc"]``
        name (str): A filename.

    Returns:
        bool: `True` if the name matches at least one of the patterns.

    """
    if not patterns:
        return True
    return any(imatch(pattern, name, accept_prefix) for pattern in patterns)


def get_matcher(patterns, case_sensitive, accept_prefix=False):
    # type: (Iterable[Text], bool, bool) -> Callable[[Text], bool]
    """Get a callable that matches names against the given patterns.

    Arguments:
        patterns (list): A list of wildcard pattern. e.g. ``["*.py",
            "*.pyc"]``
        case_sensitive (bool): If ``True``, then the callable will be case
            sensitive, otherwise it will be case insensitive.
        accept_prefix (bool): If ``True``, then the callable will not only
            find perfect matches but also strings that can be extended
            to perfect matches.

    Returns:
        callable: a matcher that will return `True` if the name given as
        an argument matches any of the given patterns.

    Example:
        >>> from fs import wildcard
        >>> is_python = wildcard.get_matcher(['*.py'], True)
        >>> is_python('__init__.py')
        True
        >>> is_python('foo.txt')
        False

    """
    if not patterns:
        return lambda name: True
    if case_sensitive:
        return lambda name: match_any(patterns, name, accept_prefix)
    else:
        return lambda name: imatch_any(patterns, name, accept_prefix)


class PatternMatcher:
    def __init__(self, pattern, case_sensitive, accept_prefixes):
        self.case_sensitive = case_sensitive
        self.accept_prefixes = accept_prefixes

        self.tokens = []
        i = 0
        while i < len(pattern):
            if pattern[i] == "[":
                start = i
                i = pattern.find("]", i) + 1
                self.tokens.append(_PatternMatcherToken(pattern[start:i]))
            elif pattern[i] == "]":
                raise ValueError(pattern + " is not a valid wildcard pattern. (unmatched ])")
            elif pattern[i] == "?":
                self.tokens.append(_PatternMatcherToken("?"))
                i += 1
            elif pattern[i] == "*":
                asterik_len = 1
                while (asterik_len + i) < len(pattern) and pattern[asterik_len + i] == "*":
                    asterik_len += 1
                if asterik_len > 2:
                    raise ValueError(pattern + " is not a valid wildcard pattern. (sequence of three or more *)")
                self.tokens.append(_PatternMatcherToken("*" * asterik_len))
                i += asterik_len
            else:
                self.tokens.append(_PatternMatcherToken(pattern[i]))
                i += 1

    def __call__(self, text):
        return self._match(self.tokens, text)

    def _match(self, tokens, text):
        if not tokens:
            return text == ""
        if not text:
            return self.accept_prefixes

        match_count = tokens[0].match(text[0], self.case_sensitive)
        if match_count == 0:
            return False
        elif match_count == 1:
            return self._match(tokens[1:], text[1:])
        else:
            return self._match(tokens[1:], text[1:]) or self._match(tokens, text[1:])


class _PatternMatcherToken:
    def __init__(self, token_str):
        self.token_str = token_str

    def __repr__(self):
        return "_PatternMatcherToken (" + self.token_str + ")"

    def match(self, character, case_sensitive):
        if self.token_str[0] == "[":
            if self.token_str[1] == "!":
                matches = self.token_str[2:-1]
                return 0 if character in matches else 1
            else:
                matches = self.token_str[1:-1]
                return 1 if character in matches else 0

        if self.token_str == "?":
            return 1

        if self.token_str == "*":
            return 2 if character != "/" else 0

        if self.token_str == "**":
            return 2

        if case_sensitive:
            return 1 if self.token_str == character else 0
        else:
            return 1 if self.token_str.lower() == character.lower() else 0
