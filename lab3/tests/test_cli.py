import io
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

    def test_encrypt_shows_matrix_pairs_and_result(self):
        out = run_cli("1", "criptografie", "cifrul", "0")
        self.assertIn(" C  R  I  P  T  O  G  A", out)
        self.assertIn(" Ț  U  V  W  X  Y  Z  *", out)
        self.assertShows(out, "prepared", "CIFRUL")
        self.assertShows(out, "pairs", "CI FR UL")
        self.assertShows(out, "ciphertext", "RPECVK")
        self.assertTrue(out.rstrip().endswith("bye"))

    def test_decrypt(self):
        out = run_cli("2", "criptografie", "rp ec vk", "0")
        self.assertShows(out, "decrypted pairs", "CI FR UL")
        self.assertShows(out, "plaintext", "CIFRUL")
        self.assertIn("restored by hand", out)

    def test_double_letters_show_the_separator(self):
        out = run_cli("1", "criptografie", "aceeași", "0")
        self.assertShows(out, "pairs", "AC EQ EA ȘI")

    def test_short_key_is_asked_again(self):
        out = run_cli("1", "cheie", "abc def", "criptografie", "a", "0")
        self.assertIn("✗ the key has 5 letters", out)
        self.assertIn("✗ the key has 6 letters", out)
        self.assertIn("at least 7 letters", out)

    def test_invalid_characters_are_asked_again(self):
        out = run_cli("1", "parola123", "criptografie", "Salut, lume!", "Anul 2026", "salut", "0")
        self.assertIn("✗ invalid character '1' at position 7", out)
        self.assertIn("✗ invalid character ',' at position 6", out)
        self.assertIn("✗ invalid character '2' at position 6", out)
        self.assertIn("Allowed: A-Z, a-z", out)
        self.assertShows(out, "prepared", "SALUT")

    def test_invalid_cryptogram_is_asked_again(self):
        out = run_cli("2", "criptografie", "ABC", "ABCC", "A!", "RPECVK", "0")
        self.assertIn("✗ a cryptogram has an even number", out)
        self.assertIn("✗ pair 2 is CC", out)
        self.assertIn("✗ invalid character '!'", out)
        self.assertShows(out, "plaintext", "CIFRUL")

    def test_invalid_menu_option(self):
        out = run_cli("5", "0")
        self.assertIn("✗ invalid option '5'; choose 1, 2 or 0.", out)

    def test_end_of_input_exits_cleanly(self):
        out = run_cli("1", EOFError())
        self.assertTrue(out.rstrip().endswith("bye"))


if __name__ == "__main__":
    unittest.main()
