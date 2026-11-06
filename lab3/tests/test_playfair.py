import random
import unittest

from alphabet import ROMANIAN_ALPHABET
from playfair import (
    FILLER,
    build_matrix,
    decrypt,
    decrypt_pairs,
    encrypt,
    encrypt_pairs,
    split_into_pairs,
)

# Section 3.2.3 of the lab: English, 5 x 5 matrix, no J, separators X and Z.
ENGLISH_NO_J = tuple("ABCDEFGHIKLMNOPQRSTUVWXYZ")
FIRST_AMENDMENT_MATRIX = (
    tuple("FIRST"),
    tuple("AMEND"),
    tuple("BCGHK"),
    tuple("LOPQU"),
    tuple("VWXYZ"),
)
CIPHERTEXT = (
    "OWEHEGRYTYNQBVOAEMGDMQVBXINRXGKISMBEDNTFBLOF"
    "NQENDSLIEGOFCRQMPIXEQCFCRFSMKRISGRDXGRGEOMRNSK"
    "GEMPILFEGFSREKSMKRGNISGRNAWCLIRQGRMGCQIPIFGNXE"
    "NRIQSFGNSRHKIUIFGNXGPQPAXGMBNMLVZSLMRYRNACPAM"
    "DKDPQDRRFMWDSGNCPXASEENDSILFEEGETNRIQRBSRAXMDG"
    "MFH"
)
DECRYPTED_PAIRS = (
    "CO NG RE SX SZ SH AL LM MA KE NO LA WR ES PE CT IN GA NE ST "
    "AB LI SH ME NT OF RE LI GI ON OR PR OH IB IT IN GT FR EX EZ EX "
    "ER CI SE TH ER EO FO RA BR RI DG IN GT HE FR EX ED OM OF SP "
    "EX EC HO RO FT HE PR ES SO RT HE RI GH TO FT HE PE OP LE PE "
    "AC EA BL YT OA SX SE MB LE AN DT OP ET IT IO NT HE GO VE RN "
    "ME NT FO RA RE DR ES SO FG RI EV AN CE SB"
)


def first_amendment_matrix():
    return build_matrix("FIRSTAMENDMENT", ENGLISH_NO_J, 5, 5)


class TestLabExample(unittest.TestCase):
    def test_matrix(self):
        self.assertEqual(first_amendment_matrix(), FIRST_AMENDMENT_MATRIX)

    def test_decrypting_the_labs_cryptogram(self):
        pairs = [CIPHERTEXT[i:i + 2] for i in range(0, len(CIPHERTEXT), 2)]
        self.assertEqual(" ".join(decrypt_pairs(pairs, first_amendment_matrix())),
                         DECRYPTED_PAIRS)

    def test_encrypting_the_labs_pairs(self):
        self.assertEqual("".join(encrypt_pairs(DECRYPTED_PAIRS.split(), first_amendment_matrix())),
                         CIPHERTEXT)

    def test_splitting_the_labs_doubles(self):
        # The lab's full list of pairs has copying slips (an extra M in "SHALL MAKE", a
        # lost HE after "PROHIBITING"), so the rule is checked on its correct segments.
        for text, expected in [
            ("CONGRESSSHAL", "CO NG RE SX SZ SH AL"),
            ("FREEEXERCISE", "FR EX EZ EX ER CI SE"),
            ("FREEDOM", "FR EX ED OM"),
            ("SPEECHO", "SP EX EC HO"),
            ("ESSOR", "ES SO RX"),
        ]:
            self.assertEqual(" ".join(split_into_pairs(text, separators=("X", "Z"))), expected)

    def test_labs_padding_letter(self):
        self.assertEqual(split_into_pairs("ANCES", separators=("X", "Z"), padding="B"),
                         ["AN", "CE", "SB"])

    def test_rules_named_in_the_lab(self):
        matrix = first_amendment_matrix()
        self.assertEqual(encrypt_pairs(["NP"], matrix), ["EQ"])  # rectangle
        self.assertEqual(encrypt_pairs(["IT"], matrix), ["RF"])  # same row, wraps
        self.assertEqual(encrypt_pairs(["CW"], matrix), ["OI"])  # same column, wraps
        self.assertEqual(decrypt_pairs(["EQ"], matrix), ["NP"])
        self.assertEqual(decrypt_pairs(["RF"], matrix), ["IT"])
        self.assertEqual(decrypt_pairs(["OI"], matrix), ["CW"])


class TestMatrix(unittest.TestCase):
    def test_hand_built_matrix(self):
        self.assertEqual(build_matrix("CRIPTOGRAFIE"), (
            ("C", "R", "I", "P", "T", "O", "G", "A"),
            ("F", "E", "Ă", "Â", "B", "D", "H", "Î"),
            ("J", "K", "L", "M", "N", "Q", "S", "Ș"),
            ("Ț", "U", "V", "W", "X", "Y", "Z", "*"),
        ))

    def test_repeated_key_letters_are_dropped(self):
        self.assertEqual("".join(build_matrix("DUBLURA")[0][:6]), "DUBLRA")

    def test_every_letter_once_for_any_key(self):
        for key in ("ȘȚÎÂĂZYX", "AAAAAAA", "".join(ROMANIAN_ALPHABET), "CRIPTOGRAFIE"):
            cells = [cell for row in build_matrix(key) for cell in row]
            self.assertEqual(sorted(cells), sorted(list(ROMANIAN_ALPHABET) + [FILLER]), key)
            self.assertEqual(cells[-1], FILLER)

    def test_matrix_too_small(self):
        with self.assertRaises(ValueError):
            build_matrix("ABCDEFG", ROMANIAN_ALPHABET, 5, 6)


class TestPairs(unittest.TestCase):
    def test_plain_split(self):
        self.assertEqual(split_into_pairs("ABCD"), ["AB", "CD"])

    def test_double_gets_a_separator(self):
        self.assertEqual(split_into_pairs("ACEEAȘ"), ["AC", "EQ", "EA", "ȘQ"])

    def test_triple_alternates_separators(self):
        self.assertEqual(split_into_pairs("EEEA"), ["EQ", "EW", "EA"])

    def test_double_of_the_separator_itself(self):
        self.assertEqual(split_into_pairs("QQ"), ["QW", "QW"])
        self.assertEqual(split_into_pairs("WW"), ["WQ", "WQ"])

    def test_padding_differs_from_last_letter(self):
        self.assertEqual(split_into_pairs("A"), ["AQ"])
        self.assertEqual(split_into_pairs("Q"), ["QW"])

    def test_no_pair_has_two_equal_letters(self):
        rng = random.Random(1)
        for _ in range(300):
            text = "".join(rng.choices("AQW", k=rng.randint(1, 30)))
            for pair in split_into_pairs(text):
                self.assertEqual(len(pair), 2)
                self.assertNotEqual(pair[0], pair[1], text)


class TestRomanianCipher(unittest.TestCase):
    KEY = "CRIPTOGRAFIE"

    def test_hand_worked_example(self):
        # Matrix in TestMatrix. CI: same row -> RP. FR: rectangle -> EC. UL: rectangle -> VK.
        result = encrypt("CIFRUL", self.KEY)
        self.assertEqual(result.pairs, ("CI", "FR", "UL"))
        self.assertEqual(result.ciphertext, "RPECVK")
        self.assertEqual(decrypt("RPECVK", self.KEY), "CIFRUL")

    def test_wrap_around_in_row_and_column(self):
        matrix = build_matrix(self.KEY)
        self.assertEqual(encrypt_pairs(["GA"], matrix), ["AC"])  # the row wraps
        self.assertEqual(encrypt_pairs(["CȚ"], matrix), ["FC"])  # the column wraps
        self.assertEqual(decrypt_pairs(["AC"], matrix), ["GA"])
        self.assertEqual(decrypt_pairs(["FC"], matrix), ["CȚ"])

    def test_filler_can_appear_and_still_decrypts(self):
        result = encrypt("YZ", self.KEY)  # same row, Z is next to the filler
        self.assertEqual(result.ciphertext, "Z*")
        self.assertEqual(decrypt("Z*", self.KEY), "YZ")

    def test_decrypting_into_the_filler_is_rejected(self):
        # Ș and A share the last column; decrypting moves A up, onto the filler below it.
        with self.assertRaisesRegex(ValueError, "cannot come from this key"):
            decrypt("ȘA", self.KEY)

    def test_round_trip_of_random_text(self):
        rng = random.Random(7)
        letters = "".join(ROMANIAN_ALPHABET)
        for _ in range(500):
            key = "".join(rng.choices(letters, k=rng.randint(7, 40)))
            text = "".join(rng.choices(letters, k=rng.randint(1, 80)))
            result = encrypt(text, key)
            self.assertEqual(decrypt(result.ciphertext, key), "".join(result.pairs))

    def test_reversing_a_pair_reverses_its_ciphertext(self):
        matrix = build_matrix(self.KEY)
        cells = [cell for row in matrix for cell in row]
        for first in cells:
            for second in cells:
                if first != second:
                    forward = encrypt_pairs([first + second], matrix)[0]
                    backward = encrypt_pairs([second + first], matrix)[0]
                    self.assertEqual(backward, forward[::-1])

    def test_a_letter_never_encrypts_to_itself(self):
        matrix = build_matrix(self.KEY)
        cells = [cell for row in matrix for cell in row]
        for first in cells:
            for second in cells:
                if first != second:
                    pair = encrypt_pairs([first + second], matrix)[0]
                    self.assertNotEqual(pair[0], first)
                    self.assertNotEqual(pair[1], second)

    def test_every_pair_is_a_bijection(self):
        """Over all pairs of different cells, decrypting undoes encrypting."""
        matrix = build_matrix(self.KEY)
        cells = [cell for row in matrix for cell in row]
        for first in cells:
            for second in cells:
                if first != second:
                    pair = first + second
                    self.assertEqual(decrypt_pairs(encrypt_pairs([pair], matrix), matrix), [pair])


if __name__ == "__main__":
    unittest.main()
