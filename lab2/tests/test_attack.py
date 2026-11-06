"""Checks the attack on variant 19. The ciphertext is not in the repository, so
the tests that need it are skipped until extract_variant.py has created it."""

import re
import unittest

from attack import (
    CIPHERTEXT_FILE,
    DICTIONARY_FILE,
    STEPS,
    apply_key,
    build_key,
    dictionary_words,
    english_share,
    is_known,
    is_two_joined_words,
)
from cryptanalysis import letter_frequencies, ngram_counts, doubled_letters, word_counts


class TestSteps(unittest.TestCase):
    def test_no_letter_is_assigned_twice(self):
        key = build_key()
        made = sum(len(substitutions) for substitutions, _ in STEPS)
        self.assertEqual(len(key), made)
        self.assertEqual(len(set(key.values())), made)

    def test_key_can_be_built_in_stages(self):
        self.assertEqual(build_key(STEPS[:1]), {"V": "E", "W": "T"})

    def test_every_step_explains_itself(self):
        for substitutions, reason in STEPS:
            self.assertTrue(substitutions)
            self.assertTrue(reason)


class TestEnglishCheck(unittest.TestCase):
    WORDS = {"CODE", "BOOK", "BREAK", "SECRET"}

    def test_common_endings(self):
        for word in ("CODE", "CODES", "CODED", "CODING", "BOOKS", "SECRETLY"):
            self.assertTrue(is_known(word, self.WORDS), word)
        self.assertFalse(is_known("XYZZY", self.WORDS))

    def test_joined_words(self):
        self.assertTrue(is_two_joined_words("CODEBOOK", self.WORDS))
        self.assertFalse(is_two_joined_words("CODEXYZ", self.WORDS))

    def test_share(self):
        found, joined, total, unknown = english_share("code codebook xyzzy", self.WORDS)
        self.assertEqual((found, joined, total, unknown), (1, 1, 3, ["XYZZY"]))


@unittest.skipUnless(CIPHERTEXT_FILE.is_file(), "data/V19.txt has not been extracted")
class TestVariant19(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CIPHERTEXT_FILE.read_text(encoding="utf-8")
        cls.words = dict(word_counts(cls.text))

    def test_frequencies_quoted_in_step_1(self):
        rows = letter_frequencies(self.text)
        self.assertEqual([letter for letter, _, _ in rows[:2]], ["V", "W"])
        self.assertAlmostEqual(rows[0][2], 12.9, delta=0.05)
        self.assertAlmostEqual(rows[1][2], 10.0, delta=0.05)

    def test_word_counts_quoted_in_the_steps(self):
        expected = {"WQV": 44, "T": 16, "WQTW": 16, "TGO": 11, "NC": 16, "WN": 8, "XG": 12,
                    "XW": 12, "XP": 7, "CNI": 8, "RTP": 4, "AV": 12, "ADW": 5, "ZDPW": 4,
                    "QTKV": 3, "LVF": 7}
        for word, count in expected.items():
            self.assertEqual(self.words[word], count, word)

    def test_rankings_quoted_in_the_steps(self):
        self.assertEqual(word_counts(self.text)[0][0], "WQV")
        self.assertEqual(word_counts(self.text, 1), [("T", 16)])
        self.assertEqual(word_counts(self.text, 2)[0], ("NC", 16))
        self.assertEqual(word_counts(self.text, 3)[1][0], "TGO")
        self.assertEqual([pair for pair, _ in ngram_counts(self.text, 2)[:2]], ["WQ", "QV"])
        self.assertEqual(dict(ngram_counts(self.text, 3))["XGJ"], 13)
        self.assertEqual(doubled_letters(self.text)[0][1], 13)
        self.assertIn(("SS", 13), doubled_letters(self.text))

    def test_partial_readings_quoted_in_the_steps(self):
        """Each `XYZ reads aBc` in a step's reason is what the text shows at that step."""
        for number, (_, reason) in enumerate(STEPS, start=1):
            key_before = build_key(STEPS[:number - 1])
            for cipher, partial in re.findall(r"\b([A-Z]{2,}) (?:\([^)]*\) )?(?:then )?reads (\w+)", reason):
                shown = apply_key(cipher, key_before)
                with self.subTest(step=number, word=cipher):
                    # Letters solved earlier in the same step may already be applied.
                    self.assertEqual(len(shown), len(partial))
                    for got, quoted in zip(shown, partial):
                        if got.islower():
                            self.assertEqual(got, quoted)
                    self.assertIn(cipher, self.text.upper())

    def test_every_letter_in_the_text_is_decided(self):
        plaintext = apply_key(self.text, build_key())
        self.assertIsNone(re.search(r"[A-Z]", plaintext))

    def test_only_cipher_letter_m_is_unused(self):
        unused = [letter for letter, count, _ in letter_frequencies(self.text) if count == 0]
        self.assertEqual(unused, ["M"])
        self.assertNotIn("M", build_key())

    @unittest.skipUnless(DICTIONARY_FILE.is_file(), "no system dictionary")
    def test_result_is_english(self):
        plaintext = apply_key(self.text, build_key())
        found, joined, total, unknown = english_share(plaintext, dictionary_words())
        self.assertGreater((found + joined) / total, 0.97)
        self.assertLessEqual(len(set(unknown)), 5)


if __name__ == "__main__":
    unittest.main()
