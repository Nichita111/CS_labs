"""Helpers for a frequency-analysis attack on a monoalphabetic cipher (English)."""

import re
import string
from collections import Counter

ALPHABET = string.ascii_uppercase

# Table 2.2 of the lab: letter frequencies of English, in percent.
ENGLISH_FREQUENCY = {
    "A": 8.17, "B": 1.49, "C": 2.78, "D": 4.25, "E": 12.70, "F": 2.23, "G": 2.01,
    "H": 6.09, "I": 6.97, "J": 0.15, "K": 0.77, "L": 4.03, "M": 2.41, "N": 6.75,
    "O": 7.51, "P": 1.93, "Q": 0.09, "R": 5.99, "S": 6.33, "T": 9.06, "U": 2.76,
    "V": 0.98, "W": 2.36, "X": 0.15, "Y": 1.97, "Z": 0.07,
}


def letters_of(text):
    """The text as uppercase Latin letters only; everything else was not encrypted."""
    return [char for char in text.upper() if char in ALPHABET]


def letter_counts(text):
    """How many times each of the 26 letters occurs, most frequent first."""
    counts = Counter({letter: 0 for letter in ALPHABET})
    counts.update(letters_of(text))
    return counts.most_common()


def letter_frequencies(text):
    """(letter, count, percent) for each of the 26 letters, most frequent first."""
    total = len(letters_of(text))
    return [(letter, count, 100 * count / total) for letter, count in letter_counts(text)]


def words_of(text):
    """Runs of letters, uppercased; an apostrophe ends a word."""
    return re.findall(r"[A-Z]+", text.upper())


def word_counts(text, length=None):
    """The most frequent words, optionally only those of the given length."""
    words = words_of(text)
    if length is not None:
        words = [word for word in words if len(word) == length]
    return Counter(words).most_common()


def ngram_counts(text, n):
    """The most frequent digraphs (n = 2) or trigraphs (n = 3) inside words."""
    counts = Counter()
    for word in words_of(text):
        counts.update(word[i:i + n] for i in range(len(word) - n + 1))
    return counts.most_common()


def doubled_letters(text):
    """Letters that occur twice in a row inside a word, most frequent first."""
    return [(pair, count) for pair, count in ngram_counts(text, 2) if pair[0] == pair[1]]


def apply_key(text, key):
    """Replace ciphertext letters using `key` ({cipher letter: plain letter}).

    As in the lab's worked example, decided letters become lowercase and
    undecided ones stay uppercase, so the partial plaintext is easy to read.
    Characters that are not letters were never encrypted and are kept.
    """
    result = []
    for char in text:
        upper = char.upper()
        if upper not in ALPHABET:
            result.append(char)
        elif upper in key:
            result.append(key[upper].lower())
        else:
            result.append(upper)
    return "".join(result)


def recovered_alphabet(key):
    """Table 2.5 of the lab: rows (cipher letter, plain letter), '?' if undecided."""
    return [(letter, key.get(letter, "?")) for letter in ALPHABET]


def encryption_key(key):
    """The key as the sender used it: {plain letter: cipher letter}."""
    return {plain: cipher for cipher, plain in key.items()}


def match_score(text):
    """Distance from English: mean absolute difference of the sorted frequencies."""
    observed = sorted((percent for _, _, percent in letter_frequencies(text)), reverse=True)
    expected = sorted(ENGLISH_FREQUENCY.values(), reverse=True)
    return sum(abs(a - b) for a, b in zip(observed, expected)) / len(ALPHABET)
