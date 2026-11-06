import unicodedata
import unittest

from validation import parse_ciphertext, parse_key, parse_message


class TestKey(unittest.TestCase):
    def test_valid_keys(self):
        self.assertEqual(parse_key("criptografie"), "CRIPTOGRAFIE")
        self.assertEqual(parse_key("abcdefg"), "ABCDEFG")  # exactly 7
        self.assertEqual(parse_key("First Amendment"), "FIRSTAMENDMENT")
        self.assertEqual(parse_key("învăţământ"), "ÎNVĂȚĂMÂNT")

    def test_length_counts_letters_not_spaces(self):
        with self.assertRaisesRegex(ValueError, "has 6 letters.*at least 7"):
            parse_key("abc def")

    def test_invalid_characters_name_the_range(self):
        for raw, char in [("parola123", "'1'"), ("parolă!!", "'!'")]:
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, f"invalid character {char}.*A-Z, a-z"):
                    parse_key(raw)

    def test_empty(self):
        with self.assertRaisesRegex(ValueError, "at least one letter"):
            parse_key("   ")


class TestMessage(unittest.TestCase):
    def test_uppercase_no_spaces(self):
        self.assertEqual(parse_message("Știința și tehnica"), "ȘTIINȚAȘITEHNICA")

    def test_cedilla_and_decomposed_letters(self):
        self.assertEqual(parse_message("ş ţ Ş Ţ"), "ȘȚȘȚ")
        self.assertEqual(parse_message(unicodedata.normalize("NFD", "știință")), "ȘTIINȚĂ")

    def test_rejected_characters(self):
        for char in [",", "!", "1", "ß", "ı", "ſ", "é", "\t", "-", "*"]:
            with self.subTest(char=char):
                with self.assertRaises(ValueError) as caught:
                    parse_message(f"ab{char}cd")
                self.assertIn(repr(char), str(caught.exception))
                self.assertIn("position 3", str(caught.exception))
                self.assertIn("A-Z, a-z", str(caught.exception))


class TestCiphertext(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_ciphertext("rp ec vk"), "RPECVK")
        self.assertEqual(parse_ciphertext("Z*"), "Z*")

    def test_odd_length(self):
        with self.assertRaisesRegex(ValueError, "even number.*has 3"):
            parse_ciphertext("ABC")

    def test_double_inside_a_pair(self):
        with self.assertRaisesRegex(ValueError, "pair 2 is CC"):
            parse_ciphertext("ABCC")

    def test_double_across_pairs_is_fine(self):
        self.assertEqual(parse_ciphertext("ABBC"), "ABBC")

    def test_invalid_character_names_the_symbol_too(self):
        with self.assertRaisesRegex(ValueError, r"'1'.*the symbol \*"):
            parse_ciphertext("A1")


if __name__ == "__main__":
    unittest.main()
