"""Parsers for user input. Each one returns the parsed value or raises
ValueError with a message that states what is allowed."""

import string

from des import hex_to_bits

HEX_DIGITS = set(string.hexdigits)
BLOCK_HINT = "8 hex digits (e.g. CC00CCFF) or 32 bits (e.g. 1100 1100 0000 ...)"


def parse_menu_option(raw, options=("0", "1", "2", "3")):
    option = raw.strip()
    if option not in options:
        raise ValueError(f"invalid option {option!r}; choose {', '.join(options[1:])} or 0.")
    return option


def parse_round(raw):
    text = raw.strip()
    if not text.isdigit() or not 1 <= int(text) <= 16:
        raise ValueError(f"{text!r} is not a round of DES; enter a number from 1 to 16.")
    return int(text)


def parse_half_block(raw):
    """32 bits, typed as 8 hex digits or as 32 binary digits; spaces are ignored."""
    text = "".join(raw.split())
    if text[:2].lower() == "0x":
        text = text[2:]
    if not text:
        raise ValueError(f"the value is empty; enter {BLOCK_HINT}.")
    if set(text) <= {"0", "1"} and len(text) == 32:
        return text
    if set(text) <= {"0", "1"} and len(text) > 8:
        raise ValueError(f"{len(text)} binary digits; a half-block has exactly 32 bits.")
    bad = next((char for char in text if char not in HEX_DIGITS), None)
    if bad is not None:
        raise ValueError(f"invalid character {bad!r}; enter {BLOCK_HINT}.")
    if len(text) != 8:
        raise ValueError(f"{len(text)} hex digits; a half-block has exactly 8 (32 bits).")
    return hex_to_bits(text)


def parse_block_text(raw):
    """Exactly 8 printable ASCII characters (spaces count), as in the lab: 8 symbols = 64 bits."""
    if len(raw) != 8:
        raise ValueError(f"{len(raw)} characters; a DES block is exactly 8 characters (64 bits).")
    bad = next((char for char in raw if not " " <= char <= "~"), None)
    if bad is not None:
        raise ValueError(f"{bad!r} is not a printable ASCII character (codes 32-126).")
    return raw
