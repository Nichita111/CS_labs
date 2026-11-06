import unittest

from alphabet import ROMANIAN_ALPHABET
from cipher import (
    brute_force,
    build_permuted_alphabet,
    decrypt,
    decrypt_with_keyword,
    encrypt,
    encrypt_with_keyword,
)

ENGLISH = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class TestExamplesFromTheLab(unittest.TestCase):
    """Test vectors from the lab statement (English alphabet, n = 26)."""

    def test_caesar_k3(self):
        self.assertEqual(encrypt("CIFRULCEZAR", 3, ENGLISH), "FLIUXOFHCDU")
        self.assertEqual(decrypt("FLIUXOFHCDU", 3, ENGLISH), "CIFRULCEZAR")

    def test_table_1(self):
        self.assertEqual(encrypt("".join(ENGLISH), 3, ENGLISH),
                         "DEFGHIJKLMNOPQRSTUVWXYZABC")

    def test_caesar_k17(self):
        self.assertEqual(encrypt("BRUTEFORCEATTACK", 17, ENGLISH), "SILKVWFITVRKKRTB")

    def test_brute_force_candidates(self):
        candidates = dict(brute_force("SILKVWFITVRKKRTB", ENGLISH))
        self.assertEqual(sorted(candidates), list(range(1, 26)))
        self.assertEqual(candidates[1], "RHKJUVEHSUQJJQSA")
        self.assertEqual(candidates[13], "FVYXIJSVGIEXXEGO")
        self.assertEqual(candidates[17], "BRUTEFORCEATTACK")
        self.assertEqual(candidates[25], "TJMLWXGJUWSLLSUC")

    def test_permuted_alphabet_cryptography(self):
        self.assertEqual("".join(build_permuted_alphabet("CRYPTOGRAPHY", ENGLISH)),
                         "CRYPTOGAHBDEFIJKLMNQSUVWXZ")

    def test_caesar_with_keyword(self):
        self.assertEqual(encrypt_with_keyword("CIFRULCEZAR", 3, "CRYPTOGRAPHY", ENGLISH),
                         "PLKTXQPJYDT")
        self.assertEqual(decrypt_with_keyword("PLKTXQPJYDT", 3, "CRYPTOGRAPHY", ENGLISH),
                         "CIFRULCEZAR")


class TestRomanianCaesar(unittest.TestCase):
    def test_hand_worked_examples(self):
        # C=4->7=F, I=10->13=K, F=7->10=I, R=20->23=T, U=25->28=X, L=14->17=O,
        # E=6->9=H, Z=30->33 mod 31=2=Â, A=0->3=B
        self.assertEqual(encrypt("CIFRULCEZAR", 3), "FKITXOFHÂBT")
        # Ș=22->25=U, T=23->26=V, N=16->19=Q, Ț=24->27=W, Ă=1->4=C
        self.assertEqual(encrypt("ȘTIINȚĂ", 3), "UVKKQWC")

    def test_wrap_around(self):
        self.assertEqual(encrypt("Z", 1), "A")
        self.assertEqual(decrypt("A", 1), "Z")
        self.assertEqual(decrypt("Ă", 3), "Y")  # (1 - 3) mod 31 = 29

    def test_shift_rotates_the_alphabet(self):
        letters = "".join(ROMANIAN_ALPHABET)
        for key in range(1, 31):
            with self.subTest(key=key):
                self.assertEqual(encrypt(letters, key), letters[key:] + letters[:key])

    def test_round_trip_every_key(self):
        text = "".join(ROMANIAN_ALPHABET) + "ȘTIINȚAȘITEHNICAÎNȚARAROMÂNEASCĂ"
        for key in range(1, 31):
            with self.subTest(key=key):
                ciphertext = encrypt(text, key)
                self.assertNotEqual(ciphertext, text)
                self.assertEqual(decrypt(ciphertext, key), text)

    def test_brute_force_finds_the_message(self):
        candidates = dict(brute_force(encrypt("ȘTIINȚĂ", 19)))
        self.assertEqual(len(candidates), 30)
        self.assertEqual(candidates[19], "ȘTIINȚĂ")


class TestRomanianPermutation(unittest.TestCase):
    def test_permuted_alphabet(self):
        permuted = build_permuted_alphabet("CRIPTOGRAFIE")
        self.assertEqual("".join(permuted), "CRIPTOGAFEĂÂBDHÎJKLMNQSȘȚUVWXYZ")
        self.assertEqual(sorted(permuted), sorted(ROMANIAN_ALPHABET))

    def test_keyword_with_diacritics(self):
        permuted = build_permuted_alphabet("ȘTIINȚĂMÂȘ")
        self.assertEqual("".join(permuted[:8]), "ȘTINȚĂMÂ")
        self.assertEqual(len(permuted), 31)
        self.assertEqual(set(permuted), set(ROMANIAN_ALPHABET))

    def test_hand_worked_example(self):
        # C(0)->P(3), I(2)->O(5), F(8)->Â(11), R(1)->T(4), U(25)->X(28),
        # L(18)->Q(21), E(9)->B(12), Z(30)->I(2), A(7)->Ă(10)
        self.assertEqual(encrypt_with_keyword("CIFRULCEZAR", 3, "CRIPTOGRAFIE"),
                         "POÂTXQPBIĂT")

    def test_round_trip_every_key(self):
        text = "".join(ROMANIAN_ALPHABET)
        for key in range(1, 31):
            with self.subTest(key=key):
                ciphertext = encrypt_with_keyword(text, key, "CRIPTOGRAFIE")
                self.assertEqual(decrypt_with_keyword(ciphertext, key, "CRIPTOGRAFIE"), text)

    def test_differs_from_plain_caesar(self):
        self.assertNotEqual(encrypt_with_keyword("CIFRULCEZAR", 3, "CRIPTOGRAFIE"),
                            encrypt("CIFRULCEZAR", 3))


if __name__ == "__main__":
    unittest.main()
