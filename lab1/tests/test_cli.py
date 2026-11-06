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

    def test_task1_encrypt_and_decrypt(self):
        out = run_cli("1", "e", "3", "Cifrul Cezar", "1", "D", "3", "fkitx ofhâbt", "0")
        self.assertIn("Prepared text (uppercase, no spaces): CIFRULCEZAR", out)
        self.assertIn("Ciphertext: FKITXOFHÂBT", out)
        self.assertIn("Decrypted message: CIFRULCEZAR", out)
        self.assertTrue(out.rstrip().endswith("Bye!"))

    def test_invalid_key_is_asked_again(self):
        out = run_cli("1", "e", "0", "31", "abc", "3", "abc", "0")
        self.assertEqual(out.count("Error: invalid key"), 3)
        self.assertIn("the key must be an integer from 1 to 30. Try again.", out)
        # A=0->3=B, B=3->6=E, C=4->7=F (Ă and Â lie between A and B)
        self.assertIn("Ciphertext: BEF", out)

    def test_invalid_text_is_asked_again(self):
        out = run_cli("1", "e", "3", "Salut, lume!", "Anul 2026", "ştiinţă", "0")
        self.assertIn("Error: invalid character ',' at position 6", out)
        self.assertIn("Error: invalid character '2' at position 6", out)
        self.assertIn("Ciphertext: UVKKQWC", out)

    def test_invalid_menu_option_and_operation(self):
        out = run_cli("5", "1", "x", "e", "1", "z", "0")
        self.assertIn("Error: invalid option '5'", out)
        self.assertIn("Error: invalid operation 'x'", out)
        self.assertIn("Ciphertext: A", out)

    def test_task2_shows_permuted_alphabet(self):
        out = run_cli("2", "e", "40", "3", "cheie", "parola123", "criptografie",
                      "Cifrul Cezar", "0")
        self.assertIn("Error: invalid key 40", out)
        self.assertIn("Error: the keyword has 5 letters", out)
        self.assertIn("Error: invalid character '1'", out)
        self.assertIn("Permuted alphabet: CRIPTOGAFEĂÂBDHÎJKLMNQSȘȚUVWXYZ", out)
        self.assertIn("m   C  R  I  P  T  O  G  A  F  E  Ă  Â  B  D  H  Î", out)
        self.assertIn("c   P  T  O  G  A  F  E  Ă  Â  B  D  H  Î  J  K  L", out)
        self.assertIn("Ciphertext: POÂTXQPBIĂT", out)

    def test_task2_decrypt(self):
        out = run_cli("2", "d", "3", "criptografie", "POÂTXQPBIĂT", "0")
        self.assertIn("Decrypted message: CIFRULCEZAR", out)

    def test_brute_force(self):
        out = run_cli("3", "UVKKQWC", "0")
        self.assertIn("k= 3  ȘTIINȚĂ", out)
        self.assertIn("k=30", out)

    def test_end_of_input_exits_cleanly(self):
        out = run_cli("1", "e", EOFError())
        self.assertTrue(out.rstrip().endswith("Bye!"))


if __name__ == "__main__":
    unittest.main()
