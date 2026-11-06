"""The Romanian alphabet (n = 31) and the rules for turning raw input into
a string of its uppercase letters."""

import unicodedata

# Table 2 of the lab: the position of a letter in this tuple is its code.
ROMANIAN_ALPHABET = (
    "A", "Ă", "Â", "B", "C", "D", "E", "F", "G", "H", "I",
    "Î", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
    "Ș", "T", "Ț", "U", "V", "W", "X", "Y", "Z",
)
N = len(ROMANIAN_ALPHABET)

LETTER_TO_CODE = {letter: code for code, letter in enumerate(ROMANIAN_ALPHABET)}

# Lowercase letters in the same order as ROMANIAN_ALPHABET.
_LOWERCASE = (
    "a", "ă", "â", "b", "c", "d", "e", "f", "g", "h", "i",
    "î", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
    "ș", "t", "ț", "u", "v", "w", "x", "y", "z",
)

# Every accepted character mapped to its uppercase letter. An explicit table
# is used instead of str.upper(), which would also "accept" characters such as
# "ß" (-> "SS"), "ı" (-> "I") or "ſ" (-> "S").
TO_UPPERCASE = {letter: letter for letter in ROMANIAN_ALPHABET}
TO_UPPERCASE.update(zip(_LOWERCASE, ROMANIAN_ALPHABET))
# S and T with a cedilla are often typed instead of the comma-below letters.
TO_UPPERCASE.update({"Ş": "Ș", "ş": "Ș", "Ţ": "Ț", "ţ": "Ț"})

ALLOWED_LETTERS_HINT = "Allowed: letters A-Z, Ă, Â, Î, Ș, Ț (any case)"


def prepare_text(raw, allow_spaces=True):
    """Return `raw` as uppercase Romanian letters with spaces removed.

    Raises ValueError naming the first character that is not allowed.
    """
    # NFC joins decomposed input (e.g. "S" + combining comma below) into one letter.
    text = unicodedata.normalize("NFC", raw)
    letters = []
    for position, char in enumerate(text, start=1):
        if char == " " and allow_spaces:
            continue
        if char not in TO_UPPERCASE:
            hint = ALLOWED_LETTERS_HINT + (" and spaces" if allow_spaces else "")
            raise ValueError(f"invalid character {char!r} at position {position}. {hint}.")
        letters.append(TO_UPPERCASE[char])
    if not letters:
        raise ValueError("the text must contain at least one letter.")
    return "".join(letters)
