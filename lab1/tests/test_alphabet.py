import unittest
import unicodedata

from alphabet import LETTER_TO_CODE, N, ROMANIAN_ALPHABET, prepare_text


class TestEncoding(unittest.TestCase):
    def test_alphabet_has_31_distinct_letters(self):
        self.assertEqual(N, 31)
        self.assertEqual(len(set(ROMANIAN_ALPHABET)), 31)

    def test_codes_match_table_2(self):
        expected = {"A": 0, "Ă": 1, "Â": 2, "B": 3, "I": 10, "Î": 11, "S": 21,
                    "Ș": 22, "T": 23, "Ț": 24, "U": 25, "Z": 30}
        for letter, code in expected.items():
            self.assertEqual(LETTER_TO_CODE[letter], code, letter)

    def test_comma_below_letters_are_used(self):
        self.assertEqual(ROMANIAN_ALPHABET[22], "Ș")  # Ș
        self.assertEqual(ROMANIAN_ALPHABET[24], "Ț")  # Ț


class TestPrepareText(unittest.TestCase):
    def test_uppercase_and_remove_spaces(self):
        self.assertEqual(prepare_text("cifrul cezar"), "CIFRULCEZAR")

    def test_lowercase_diacritics(self):
        self.assertEqual(prepare_text("ă â î ș ț"), "ĂÂÎȘȚ")

    def test_cedilla_variants_become_comma_below(self):
        self.assertEqual(prepare_text("ş ţ Ş Ţ"), "ȘȚȘȚ")

    def test_decomposed_input_is_accepted(self):
        decomposed = unicodedata.normalize("NFD", "știință ÎNVĂȚĂMÂNT")
        self.assertNotEqual(decomposed, "știință ÎNVĂȚĂMÂNT")
        self.assertEqual(prepare_text(decomposed), "ȘTIINȚĂÎNVĂȚĂMÂNT")

    def test_rejected_characters(self):
        for char in [",", "!", "1", "ß", "ı", "ſ", "é", "ä", "\t", "-"]:
            with self.subTest(char=char):
                with self.assertRaises(ValueError) as ctx:
                    prepare_text(f"ab{char}cd")
                self.assertIn(repr(char), str(ctx.exception))
                self.assertIn("position 3", str(ctx.exception))

    def test_empty_text_is_rejected(self):
        for raw in ["", "   "]:
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, "at least one letter"):
                    prepare_text(raw)

    def test_spaces_can_be_forbidden(self):
        with self.assertRaisesRegex(ValueError, "' '"):
            prepare_text("ab cd", allow_spaces=False)


if __name__ == "__main__":
    unittest.main()
