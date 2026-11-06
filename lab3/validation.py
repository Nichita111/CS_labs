"""Parsers for user input. Each one returns the parsed value or raises
ValueError with a message that states what is allowed."""

from alphabet import prepare_text
from playfair import FILLER

MIN_KEY_LENGTH = 7
CIPHERTEXT_HINT = f"Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț (any case), spaces and the symbol {FILLER}"


def parse_key(raw):
    """The key: at least MIN_KEY_LENGTH letters; a short phrase is fine, spaces are dropped."""
    key = prepare_text(raw)
    if len(key) < MIN_KEY_LENGTH:
        raise ValueError(f"the key has {len(key)} letters; it must have at least "
                         f"{MIN_KEY_LENGTH} letters of the Romanian alphabet.")
    return key


def parse_message(raw):
    """A message: Romanian letters and spaces."""
    return prepare_text(raw)


def parse_ciphertext(raw):
    """A cryptogram: an even number of symbols, and never a double inside a pair."""
    text = prepare_text(raw, extra=FILLER, hint=CIPHERTEXT_HINT)
    if len(text) % 2:
        raise ValueError(f"a cryptogram has an even number of letters, this one has {len(text)}.")
    for start in range(0, len(text), 2):
        if text[start] == text[start + 1]:
            raise ValueError(f"pair {start // 2 + 1} is {text[start:start + 2]}, but Playfair "
                             "never produces two equal letters in a pair.")
    return text
