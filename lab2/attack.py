"""The frequency-analysis attack on Lab 2, variant 19, step by step.

    python3 attack.py --stats    letter, word and n-gram statistics of the ciphertext
    python3 attack.py --stages   the steps of the attack on a short fragment
    python3 attack.py --key      the recovered alphabet (Table 2.5 of the lab)
    python3 attack.py --check    how much of the result is real English
    python3 attack.py --full     the whole decrypted message

The ciphertext is read from data/V19.txt, which is not in the repository:
python3 extract_variant.py <lab PDF> 19 creates it from the lab's PDF.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from cryptanalysis import (
    ALPHABET,
    ENGLISH_FREQUENCY,
    apply_key,
    doubled_letters,
    encryption_key,
    letter_frequencies,
    letters_of,
    ngram_counts,
    recovered_alphabet,
    word_counts,
    words_of,
)

CIPHERTEXT_FILE = Path(__file__).parent / "data" / "V19.txt"
DICTIONARY_FILE = Path("/usr/share/dict/words")
FRAGMENT_WORDS = 11

# Each step: the substitutions made and the evidence for them, in attack order.
# tests/test_attack.py checks every number and partial word quoted here.
STEPS = [
    ({"V": "E", "W": "T"},
     "V (12.9%) and W (10.0%) are the two most frequent letters; "
     "E (12.7%) and T (9.06%) are the two most frequent in English."),
    ({"Q": "H"},
     "WQV is by far the most frequent word (44 times) and now reads tQe: the. "
     "WQ and QV are also the two most frequent digraphs, like TH and HE."),
    ({"T": "A"},
     "T is the only one-letter word (16 times), so it is a or i. "
     "WQTW (16 times) reads thTt: that, so T is a."),
    ({"G": "N", "O": "D"},
     "TGO is the second most frequent three-letter word (11 times) "
     "and reads aGO: and."),
    ({"N": "O", "C": "F"},
     "NC is the most frequent two-letter word (16 times). WN (8 times) reads tN: to, "
     "so N is o. NC then reads oC: of."),
    ({"X": "I", "P": "S"},
     "XG and XW (12 times each) read Xn and Xt: in and it. "
     "XP (7 times) then reads iP: is, and P is frequent (7.6%)."),
    ({"I": "R", "R": "W"},
     "CNI (8 times) reads foI: for. RTP (4 times) reads Ras: was."),
    ({"A": "B", "D": "U", "Z": "M"},
     "AV (12 times) reads Ae: be. ADW (5 times) reads bDt: but. "
     "ZDPW (4 times) reads Zust: must."),
    ({"S": "L", "F": "Y", "K": "V"},
     "TSS reads aSS: all, and SS is the joint most frequent doubled letter. "
     "ZTF reads maF: may. QTKV (3 times) reads haKe: have."),
    ({"L": "K", "U": "P", "J": "G"},
     "LVF (7 times) reads Ley: key. UTIW reads Uart: part. "
     "XGJ (13 times) is a top trigraph that reads inJ: the ending -ing."),
    ({"H": "C", "B": "Q", "Y": "X", "E": "J"},
     "The rest is almost readable. HXUQVI reads Hipher: cipher. IVBDXIVZVGWP reads "
     "reBuirements: requirements. PXY reads siY: six. WNHNGEDIV reads toconEure: to conjure."),
]


def build_key(steps=STEPS):
    """Merge the substitutions of the given steps into one key."""
    key = {}
    for substitutions, _ in steps:
        key.update(substitutions)
    return key


def read_ciphertext(path=CIPHERTEXT_FILE):
    if not path.is_file():
        sys.exit(f"{path} not found. Create it with: python3 extract_variant.py <lab PDF> 19")
    return path.read_text(encoding="utf-8")


def fragment(text, count=FRAGMENT_WORDS):
    """The first words of the text, enough to follow the attack."""
    return " ".join(text.split()[:count])


def print_stats(text):
    print(f"letters: {len(letters_of(text))}\n")
    print("cipher  count  percent     English")
    english = sorted(ENGLISH_FREQUENCY.items(), key=lambda item: -item[1])
    for (letter, count, percent), (plain, expected) in zip(letter_frequencies(text), english):
        print(f"  {letter}     {count:>4}  {percent:>6.2f}      {plain} {expected:>5.2f}")
    print("\n1-letter words  ", word_counts(text, 1)[:3])
    print("2-letter words  ", word_counts(text, 2)[:6])
    print("3-letter words  ", word_counts(text, 3)[:6])
    print("4-letter words  ", word_counts(text, 4)[:6])
    print("digraphs        ", ngram_counts(text, 2)[:6])
    print("trigraphs       ", ngram_counts(text, 3)[:6])
    print("doubled letters ", doubled_letters(text)[:6])


def print_stages(text):
    start = fragment(text)
    print(f"ciphertext: {start}\n")
    for number in range(1, len(STEPS) + 1):
        substitutions, reason = STEPS[number - 1]
        made = ", ".join(f"{c}->{p.lower()}" for c, p in substitutions.items())
        print(f"step {number}: {made}")
        print(f"  why: {reason}")
        print(f"  now: {apply_key(start, build_key(STEPS[:number]))}\n")


def print_key():
    key = build_key()
    rows = recovered_alphabet(key)
    print("cipher  " + " ".join(cipher for cipher, _ in rows))
    print("plain   " + " ".join(plain.lower() for _, plain in rows))
    sender = encryption_key(key)
    print("\nplain   " + " ".join(chr(ord("A") + i) for i in range(26)))
    print("cipher  " + " ".join(sender.get(chr(ord("A") + i), "?") for i in range(26)))
    unused = [letter for letter, count, _ in letter_frequencies(read_ciphertext()) if count == 0]
    print(f"\ncipher letters that never occur in this text: {', '.join(unused)}")
    plain_left = sorted(set(ALPHABET) - set(key.values()))
    print(f"plain letters not assigned yet: {', '.join(plain_left)}")
    if len(unused) == len(plain_left) == 1:
        print(f"so by elimination {unused[0]} -> {plain_left[0].lower()}")


def dictionary_words(path=DICTIONARY_FILE):
    return {word.strip().upper() for word in path.read_text().splitlines()}


def is_known(word, dictionary):
    """The word, or the word without a common ending, is in the dictionary."""
    if word in dictionary:
        return True
    for ending, replacement in (("S", ""), ("ES", ""), ("ED", ""), ("ED", "E"), ("ING", ""),
                                ("ING", "E"), ("LY", ""), ("IES", "Y")):
        if word.endswith(ending) and word[:-len(ending)] + replacement in dictionary:
            return True
    return False


def is_two_joined_words(word, dictionary):
    """The PDF lost some spaces at line breaks, e.g. two words printed as one."""
    return any(is_known(word[:i], dictionary) and is_known(word[i:], dictionary)
               for i in range(2, len(word) - 1))


def english_share(text, dictionary):
    """(words found, joined pairs found, all words, the words not found)."""
    found, joined, unknown = 0, 0, []
    words = words_of(text)
    for word in words:
        if is_known(word, dictionary):
            found += 1
        elif is_two_joined_words(word, dictionary):
            joined += 1
        else:
            unknown.append(word)
    return found, joined, len(words), unknown


def print_check(text):
    plaintext = apply_key(text, build_key())
    undecided = sorted(set(re.findall(r"[A-Z]", plaintext)))
    print(f"letters still undecided: {undecided or 'none'}")
    found, joined, total, unknown = english_share(plaintext, dictionary_words())
    print(f"words: {total}")
    print(f"  in the macOS dictionary:        {found} ({100 * found / total:.1f}%)")
    print(f"  two dictionary words joined:    {joined} ({100 * joined / total:.1f}%)")
    print(f"  not recognised:                 {len(unknown)} ({100 * len(unknown) / total:.1f}%)")
    print(f"  most common not recognised:     {Counter(unknown).most_common(5)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for option in ("stats", "stages", "key", "check", "full"):
        parser.add_argument(f"--{option}", action="store_true")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        return
    text = read_ciphertext()
    if args.stats:
        print_stats(text)
    if args.stages:
        print_stages(text)
    if args.key:
        print_key()
    if args.check:
        print_check(text)
    if args.full:
        print(apply_key(text, build_key()))


if __name__ == "__main__":
    main()
