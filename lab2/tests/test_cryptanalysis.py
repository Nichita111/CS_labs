import unittest

from cryptanalysis import (
    ALPHABET,
    ENGLISH_FREQUENCY,
    apply_key,
    doubled_letters,
    encryption_key,
    letter_counts,
    letter_frequencies,
    letters_of,
    ngram_counts,
    recovered_alphabet,
    word_counts,
)
from extract_variant import variant_text


class TestStatistics(unittest.TestCase):
    def test_english_table_is_complete(self):
        self.assertEqual(sorted(ENGLISH_FREQUENCY), list(ALPHABET))
        self.assertAlmostEqual(sum(ENGLISH_FREQUENCY.values()), 100, delta=0.2)

    def test_only_letters_are_counted(self):
        self.assertEqual(letters_of("Ab, c-1 '2"), ["A", "B", "C"])

    def test_letter_counts_are_sorted_and_cover_the_alphabet(self):
        counts = letter_counts("bab cab")
        self.assertEqual(counts[0], ("B", 3))
        self.assertEqual(len(counts), 26)
        self.assertEqual(dict(counts)["Z"], 0)

    def test_frequencies_sum_to_100(self):
        self.assertAlmostEqual(sum(p for _, _, p in letter_frequencies("hello world")), 100)

    def test_word_counts_by_length(self):
        self.assertEqual(word_counts("the cat. The dog", 3)[0], ("THE", 2))
        self.assertEqual(word_counts("a bb a", 1), [("A", 2)])

    def test_ngrams_do_not_cross_words(self):
        self.assertNotIn(("EC", 1), ngram_counts("the cat", 2))
        self.assertEqual(ngram_counts("thethe", 3)[0], ("THE", 2))

    def test_doubled_letters(self):
        self.assertEqual(doubled_letters("all bee less"), [("LL", 1), ("EE", 1), ("SS", 1)])


class TestKey(unittest.TestCase):
    # Part of the key the lab recovers in section 2.3 (Table 2.5).
    KEY = dict(G="O", F="N", S="E", W="W", M="A", Y="Y", O="T", L="S", D="L",
               V="V", N="C", K="R", H="P", U="D", E="M", R="G")

    def test_example_from_the_lab(self):
        self.assertEqual(apply_key("GFS WMY OG LGDVS MF SFNKYHOSU ESLLMRS", self.KEY),
                         "one way to solve an encrypted message")

    def test_undecided_letters_stay_uppercase(self):
        self.assertEqual(apply_key("GFS WMY", {"S": "E", "M": "A"}), "GFe WaY")

    def test_other_characters_are_kept(self):
        self.assertEqual(apply_key("O, 1'S — x", {"O": "T", "S": "E"}), "t, 1'e — X")

    def test_recovered_alphabet(self):
        rows = dict(recovered_alphabet({"A": "Q"}))
        self.assertEqual(rows["A"], "Q")
        self.assertEqual(rows["B"], "?")
        self.assertEqual(len(rows), 26)

    def test_encryption_key_is_the_inverse(self):
        self.assertEqual(encryption_key({"A": "Q", "B": "R"}), {"Q": "A", "R": "B"})


class TestExtractVariant(unittest.TestCase):
    PDF = "intro\nV1\nfirst line\nsecond\nV2\nthird\nV3\nlast\n\nnext page\n"

    def test_lines_between_headings(self):
        self.assertEqual(variant_text(self.PDF, 1), "first line\nsecond\n")
        self.assertEqual(variant_text(self.PDF, 2), "third\n")

    def test_last_variant_ends_at_a_blank_line(self):
        self.assertEqual(variant_text(self.PDF, 3), "last\n")

    def test_missing_variant(self):
        with self.assertRaises(ValueError):
            variant_text(self.PDF, 7)


if __name__ == "__main__":
    unittest.main()
