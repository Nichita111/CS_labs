import unittest

from validation import parse_block_text, parse_half_block, parse_menu_option, parse_round

CC00CCFF = "11001100000000001100110011111111"


class TestHalfBlock(unittest.TestCase):
    def test_hex_in_any_case_with_spaces_or_prefix(self):
        for raw in ("CC00CCFF", "cc00ccff", " CC00 CCFF ", "0xCC00CCFF", "0Xcc00ccff"):
            with self.subTest(raw=raw):
                self.assertEqual(parse_half_block(raw), CC00CCFF)

    def test_binary(self):
        self.assertEqual(parse_half_block("1100 1100 0000 0000 1100 1100 1111 1111"), CC00CCFF)
        self.assertEqual(parse_half_block(CC00CCFF), CC00CCFF)

    def test_eight_binary_digits_are_read_as_hex(self):
        self.assertEqual(parse_half_block("10101010"), "00010000" * 4)

    def test_wrong_length(self):
        with self.assertRaisesRegex(ValueError, "7 hex digits"):
            parse_half_block("CC00CCF")
        with self.assertRaisesRegex(ValueError, "9 hex digits"):
            parse_half_block("CC00CCFF0")
        with self.assertRaisesRegex(ValueError, "31 binary digits"):
            parse_half_block("1" * 31)

    def test_invalid_character(self):
        with self.assertRaisesRegex(ValueError, "invalid character 'G'"):
            parse_half_block("CC00CCFG")

    def test_empty(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            parse_half_block("   ")


class TestRound(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_round(" 1 "), 1)
        self.assertEqual(parse_round("16"), 16)

    def test_invalid(self):
        for raw in ("0", "17", "-1", "abc", "", "2.5"):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "from 1 to 16"):
                parse_round(raw)


class TestBlockText(unittest.TestCase):
    def test_exactly_eight_characters_spaces_included(self):
        self.assertEqual(parse_block_text("Lab4 DES"), "Lab4 DES")
        self.assertEqual(parse_block_text(" a b c d"), " a b c d")

    def test_wrong_length(self):
        with self.assertRaisesRegex(ValueError, "7 characters"):
            parse_block_text("short!!")
        with self.assertRaisesRegex(ValueError, "9 characters"):
            parse_block_text("too long!")

    def test_non_ascii(self):
        with self.assertRaisesRegex(ValueError, "'ș' is not a printable ASCII"):
            parse_block_text("cheieș12")
        with self.assertRaisesRegex(ValueError, "printable ASCII"):
            parse_block_text("tab\there")


class TestMenu(unittest.TestCase):
    def test_options(self):
        self.assertEqual(parse_menu_option(" 3 "), "3")
        with self.assertRaisesRegex(ValueError, "choose 1, 2, 3 or 0"):
            parse_menu_option("4")


if __name__ == "__main__":
    unittest.main()
