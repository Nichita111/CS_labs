"""Caesar cipher and Caesar cipher with a keyword-permuted alphabet.

The functions work on any alphabet given as a sequence of letters; the
numeric code of a letter is always its position in that sequence.
"""

from alphabet import ROMANIAN_ALPHABET


def _shift(text, key, alphabet):
    code_of = {letter: code for code, letter in enumerate(alphabet)}
    n = len(alphabet)
    # Python's % always returns a value in 0..n-1 for n > 0, so (y - k) mod n
    # needs no extra correction when y - k is negative.
    return "".join(alphabet[(code_of[letter] + key) % n] for letter in text)


def encrypt(text, key, alphabet=ROMANIAN_ALPHABET):
    """c = (x + k) mod n for every letter x of the text."""
    return _shift(text, key, alphabet)


def decrypt(text, key, alphabet=ROMANIAN_ALPHABET):
    """m = (y - k) mod n for every letter y of the ciphertext."""
    return _shift(text, -key, alphabet)


def build_permuted_alphabet(keyword, alphabet=ROMANIAN_ALPHABET):
    """Keyword letters first (each kept only once), then the rest of the alphabet."""
    permuted = []
    for letter in list(keyword) + list(alphabet):
        if letter not in permuted:
            permuted.append(letter)
    return tuple(permuted)


def encrypt_with_keyword(text, key, keyword, alphabet=ROMANIAN_ALPHABET):
    return encrypt(text, key, build_permuted_alphabet(keyword, alphabet))


def decrypt_with_keyword(text, key, keyword, alphabet=ROMANIAN_ALPHABET):
    return decrypt(text, key, build_permuted_alphabet(keyword, alphabet))


def brute_force(ciphertext, alphabet=ROMANIAN_ALPHABET):
    """Decrypt with every key 1..n-1, as a cryptanalyst would."""
    return [(key, decrypt(ciphertext, key, alphabet)) for key in range(1, len(alphabet))]
