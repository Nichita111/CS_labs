import io
import random
import unittest
from contextlib import redirect_stdout
from unittest import mock

import main


def run_cli(*inputs):
    """Run the program with the given lines as keyboard input; return its output."""
    output = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs)), redirect_stdout(output):
        main.main()
    return output.getvalue()


class TestCli(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(main, "USE_COLOR", False)
        patcher.start()
        self.addCleanup(patcher.stop)

    def assertShows(self, out, label, value):
        """The output has an aligned `label   value` line (not an input prompt)."""
        self.assertRegex(out, rf"(?m)^  {label}\s+{value}$")

    def test_manual_input_shows_table_and_every_step(self):
        out = run_cli("1", "1", "CC00CCFF", "0101 1100 1000 0010 1011 0101 1001 0111", "0")
        self.assertIn("Table P", out)
        self.assertIn("16   7  20  21  29  12  28  17", out)
        self.assertIn("0101 1100 1000 0010 1011 0101 1001 0111   = 5C82B597", out)
        self.assertIn("bits 16  7 20 21 29 12 28 17  →  0 0 1 0 0 0 1 1", out)
        self.assertIn("0010 0011 0100 1010 1010 1001 1011 1011   = 234AA9BB", out)
        self.assertIn("Step 3. R1 = L0 ⊕ f", out)
        self.assertIn("= R1  1110 1111 0100 1010 0110 0101 0100 0100   EF4A6544", out)
        self.assertShows(out, "R1", r"EF4A6544  \(1110 1111 0100 1010 0110 0101 0100 0100\)")
        self.assertTrue(out.rstrip().endswith("bye"))

    def test_round_number_names_the_halves(self):
        out = run_cli("1", "7", "ACEAE4EC", "DAC18A4C", "0")
        self.assertIn("Step 3. R7 = L6 ⊕ f", out)
        self.assertShows(out, "R7", r"755365CE  .*")

    def test_random_data(self):
        random.seed(2026)
        out = run_cli("2", "0")
        self.assertIn("Random data", out)
        self.assertRegex(out, r"(?m)^  round k\s+\d+$")
        self.assertRegex(out, r"(?m)^  R\d+\s+[0-9A-F]{8}  \(")

    def test_from_real_des_matches(self):
        out = run_cli("3", "Lab4 DES", "security", "3", "0")
        self.assertShows(out, "M \\(ASCII\\)", "4C 61 62 34 20 44 45 53   = 4C61623420444553")
        self.assertShows(out, "IP\\(M\\) = L0 R0", "E78869C2 001E0184")
        self.assertShows(out, "S1\\(B1\\)", r"000100: row 0, column  2 → 13 = 1101")
        self.assertShows(out, "R3", r"755365CE  .*")
        self.assertIn("✓ the same R3 as the full DES computation", out)

    def test_from_real_des_round_16(self):
        out = run_cli("3", "01234567", "12345678", "16", "0")
        self.assertIn("round 15", out)
        self.assertIn("✓ the same R16", out)

    def test_invalid_input_is_asked_again(self):
        out = run_cli("1", "0", "17", "1", "CC00CCF", "CC00CCFG", "CC00CCFF", "1" * 31, "5C82B597", "0")
        self.assertIn("✗ '0' is not a round of DES", out)
        self.assertIn("✗ '17' is not a round of DES", out)
        self.assertIn("✗ 7 hex digits", out)
        self.assertIn("✗ invalid character 'G'", out)
        self.assertIn("✗ 31 binary digits", out)
        self.assertShows(out, "R1", r"EF4A6544  .*")

    def test_invalid_block_text_is_asked_again(self):
        out = run_cli("3", "short", "Lab4 DES", "cheieș12", "security", "3", "0")
        self.assertIn("✗ 5 characters", out)
        self.assertIn("✗ 'ș' is not a printable ASCII character", out)
        self.assertIn("✓ the same R3", out)

    def test_invalid_menu_option(self):
        out = run_cli("5", "0")
        self.assertIn("✗ invalid option '5'; choose 1, 2, 3 or 0.", out)

    def test_end_of_input_exits_cleanly(self):
        out = run_cli("1", EOFError())
        self.assertTrue(out.rstrip().endswith("bye"))


if __name__ == "__main__":
    unittest.main()
