"""Parsers for user input. Each one returns the parsed value or raises
ValueError with a message that states what is allowed."""

import re

from alphabet import N, prepare_text

MIN_KEYWORD_LENGTH = 7


def parse_key(raw, n=N):
    """The shift key: an integer from 1 to n - 1."""
    allowed = f"the key must be an integer from 1 to {n - 1}."
    value = raw.strip()
    if not value:
        raise ValueError(f"no key was entered; {allowed}")
    # Only ASCII digits: rejects "-3", "3.5", "+3" and digits of other scripts.
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError(f"invalid key {value!r}; {allowed}")
    key = int(value)
    if not 1 <= key <= n - 1:
        raise ValueError(f"invalid key {key}; {allowed}")
    return key


def parse_text(raw):
    """A message or ciphertext: Romanian letters and spaces."""
    return prepare_text(raw, allow_spaces=True)


def parse_keyword(raw):
    """Key 2: at least MIN_KEYWORD_LENGTH Romanian letters, no spaces."""
    keyword = prepare_text(raw.strip(), allow_spaces=False)
    if len(keyword) < MIN_KEYWORD_LENGTH:
        raise ValueError(
            f"the keyword has {len(keyword)} letters; it must contain "
            f"at least {MIN_KEYWORD_LENGTH} letters of the Romanian alphabet."
        )
    return keyword
