"""The Romanian alphabet (n = 31) and the rules for turning raw input into
a string of its uppercase letters."""

import unicodedata

ROMANIAN_ALPHABET = (
    "A", "Ă", "Â", "B", "C", "D", "E", "F", "G", "H", "I",
    "Î", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
    "Ș", "T", "Ț", "U", "V", "W", "X", "Y", "Z",
)

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

ALLOWED_LETTERS_HINT = "Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț (any case) and spaces"


def prepare_text(raw, extra="", hint=ALLOWED_LETTERS_HINT):
    """Return `raw` as uppercase Romanian letters with spaces removed.

    Characters in `extra` are kept as they are. Raises ValueError naming the
    first character that is not allowed, and the allowed range.
    """
    # NFC joins decomposed input (e.g. "S" + combining comma below) into one letter.
    text = unicodedata.normalize("NFC", raw.strip())
    letters = []
    for position, char in enumerate(text, start=1):
        if char == " ":
            continue
        if char in extra:
            letters.append(char)
        elif char in TO_UPPERCASE:
            letters.append(TO_UPPERCASE[char])
        else:
            raise ValueError(f"invalid character {char!r} at position {position}. {hint}.")
    if not letters:
        raise ValueError(f"at least one letter is needed. {hint}.")
    return "".join(letters)
