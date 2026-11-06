import unittest

from validation import parse_key, parse_keyword, parse_text


class TestParseKey(unittest.TestCase):
    def test_valid_keys(self):
        for key in range(1, 31):
            self.assertEqual(parse_key(str(key)), key)
        self.assertEqual(parse_key("  7 "), 7)

    def test_invalid_keys(self):
        for raw in ["0", "31", "100", "-3", "+3", "abc", "3.5", "", "  ", "٣", "1 2"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError) as ctx:
                    parse_key(raw)
                self.assertIn("integer from 1 to 30", str(ctx.exception))


class TestParseText(unittest.TestCase):
    def test_valid_text(self):
        self.assertEqual(parse_text("Știința și tehnica"), "ȘTIINȚAȘITEHNICA")

    def test_invalid_character_is_named(self):
        with self.assertRaisesRegex(ValueError, "invalid character ','"):
            parse_text("Salut, lume!")


class TestParseKeyword(unittest.TestCase):
    def test_valid_keywords(self):
        self.assertEqual(parse_keyword("criptografie"), "CRIPTOGRAFIE")
        self.assertEqual(parse_keyword("abcdefg"), "ABCDEFG")  # exactly 7
        self.assertEqual(parse_keyword("învăţământ"), "ÎNVĂȚĂMÂNT")

    def test_too_short(self):
        with self.assertRaises(ValueError) as ctx:
            parse_keyword("cheie")
        self.assertIn("has 5 letters", str(ctx.exception))
        self.assertIn("at least 7", str(ctx.exception))

    def test_invalid_characters(self):
        for raw, char in [("parola123", "'1'"), ("cheie secreta", "' '"), ("parolă!", "'!'")]:
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, f"invalid character {char}"):
                    parse_keyword(raw)

    def test_empty(self):
        with self.assertRaises(ValueError):
            parse_keyword("")


if __name__ == "__main__":
    unittest.main()
