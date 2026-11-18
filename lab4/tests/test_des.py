import random
import unittest

from des import (
    bits_to_hex,
    decrypt_block,
    encrypt_block,
    hex_to_bits,
    key_schedule,
    permute,
    run_block,
    s_box,
    text_to_bits,
)
from des_tables import E, IP, IP_INVERSE, P, PC1, PC2, S_BOXES, SHIFTS


def bits(text):
    return text.replace(" ", "")


# J. Orlin Grabbe, "The DES Algorithm Illustrated": M = 0123456789ABCDEF,
# K = 133457799BBCDFF1, every intermediate value written out.
M = hex_to_bits("0123456789ABCDEF")
K = hex_to_bits("133457799BBCDFF1")


class TestTables(unittest.TestCase):
    def test_permutations_use_every_position_once(self):
        self.assertEqual(sorted(IP), list(range(1, 65)))
        self.assertEqual(sorted(IP_INVERSE), list(range(1, 65)))
        self.assertEqual(sorted(P), list(range(1, 33)))

    def test_ip_inverse_undoes_ip(self):
        block = "".join(random.choice("01") for _ in range(64))
        self.assertEqual(permute(permute(block, IP), IP_INVERSE), block)

    def test_e_repeats_the_edge_bits(self):
        self.assertEqual(len(E), 48)
        self.assertEqual(set(E), set(range(1, 33)))
        for box in range(8):  # each 6-bit group: the 4 bits of a nibble and its 2 neighbours
            self.assertEqual(E[6 * box + 1:6 * box + 5], tuple(range(4 * box + 1, 4 * box + 5)))

    def test_pc1_drops_the_parity_bits(self):
        self.assertEqual(sorted(PC1), [p for p in range(1, 65) if p % 8])

    def test_pc2_drops_eight_bits(self):
        self.assertEqual(len(set(PC2)), 48)
        self.assertEqual(set(range(1, 57)) - set(PC2), {9, 18, 22, 25, 35, 38, 43, 54})

    def test_shifts_add_up_to_a_full_turn(self):
        self.assertEqual(len(SHIFTS), 16)
        self.assertEqual(sum(SHIFTS), 28)

    def test_every_s_box_row_is_a_permutation_of_0_to_15(self):
        for box in S_BOXES:
            self.assertEqual(len(box), 4)
            for row in box:
                self.assertEqual(sorted(row), list(range(16)))


class TestKeySchedule(unittest.TestCase):
    schedule = key_schedule(K)

    def test_k_plus(self):
        self.assertEqual(self.schedule.k_plus,
                         bits("1111000 0110011 0010101 0101111 0101010 1011001 1001111 0001111"))

    def test_c_and_d(self):
        self.assertEqual(self.schedule.c[0], bits("1111000 0110011 0010101 0101111"))
        self.assertEqual(self.schedule.d[0], bits("0101010 1011001 1001111 0001111"))
        self.assertEqual(self.schedule.c[1], bits("1110000 1100110 0101010 1011111"))
        self.assertEqual(self.schedule.d[1], bits("1010101 0110011 0011110 0011110"))
        self.assertEqual(self.schedule.c[16], self.schedule.c[0])
        self.assertEqual(self.schedule.d[16], self.schedule.d[0])

    def test_round_keys(self):
        self.assertEqual(self.schedule.subkeys[0],
                         bits("000110 110000 001011 101111 111111 000111 000001 110010"))
        self.assertEqual(self.schedule.subkeys[15],
                         bits("110010 110011 110110 001011 000011 100001 011111 110101"))


class TestRounds(unittest.TestCase):
    trace = run_block(M, K)

    def test_initial_permutation(self):
        self.assertEqual(self.trace.permuted[:32], bits("1100 1100 0000 0000 1100 1100 1111 1111"))
        self.assertEqual(self.trace.permuted[32:], bits("1111 0000 1010 1010 1111 0000 1010 1010"))

    def test_round_1(self):
        first = self.trace.rounds[0]
        self.assertEqual(first.expanded, bits("011110 100001 010101 010101 011110 100001 010101 010101"))
        self.assertEqual(first.mixed, bits("011000 010001 011110 111010 100001 100110 010100 100111"))
        self.assertEqual(first.s_output, bits("0101 1100 1000 0010 1011 0101 1001 0111"))
        self.assertEqual(first.f, bits("0010 0011 0100 1010 1010 1001 1011 1011"))
        self.assertEqual(first.left, self.trace.permuted[32:])
        self.assertEqual(first.right, bits("1110 1111 0100 1010 0110 0101 0100 0100"))

    def test_s1_lookup(self):
        # Grabbe's example: B = 011011, row 01 = 1, column 1101 = 13 -> 5.
        step = s_box(1, "011011")
        self.assertEqual((step.row, step.column, step.value, step.four_bits), (1, 13, 5, "0101"))

    def test_round_16_and_output(self):
        last = self.trace.rounds[15]
        self.assertEqual(last.left, bits("0100 0011 0100 0010 0011 0010 0011 0100"))
        self.assertEqual(last.right, bits("0000 1010 0100 1100 1101 1001 1001 0101"))
        self.assertEqual(self.trace.preoutput, last.right + last.left)
        self.assertEqual(bits_to_hex(self.trace.output), "85E813540F0AB405")

    def test_each_round_takes_the_previous_halves(self):
        for before, after in zip(self.trace.rounds, self.trace.rounds[1:]):
            self.assertEqual((after.left_in, after.right_in), (before.left, before.right))


class TestKnownAnswers(unittest.TestCase):
    VECTORS = (  # key, plaintext, ciphertext
        ("133457799BBCDFF1", "0123456789ABCDEF", "85E813540F0AB405"),
        ("0E329232EA6D0D73", "8787878787878787", "0000000000000000"),
        ("0101010101010101", "8000000000000000", "95F8A5E5DD31D900"),
        ("0123456789ABCDEF", "4E6F772069732074", "3FA40E8A984D4815"),  # "Now is t"
    )

    def test_encrypt_and_decrypt(self):
        for key, plain, cipher in self.VECTORS:
            with self.subTest(key=key, plain=plain):
                self.assertEqual(bits_to_hex(encrypt_block(hex_to_bits(plain), hex_to_bits(key))), cipher)
                self.assertEqual(bits_to_hex(decrypt_block(hex_to_bits(cipher), hex_to_bits(key))), plain)

    def test_text_to_bits_uses_ascii(self):
        self.assertEqual(bits_to_hex(text_to_bits("Now is t")), "4E6F772069732074")
        with self.assertRaises(ValueError):
            text_to_bits("too short")
        with self.assertRaises(ValueError):
            text_to_bits("ăăăăăăăă")

    def test_parity_bits_are_ignored(self):
        flipped = "".join(b if (i + 1) % 8 else str(1 - int(b)) for i, b in enumerate(K))
        self.assertEqual(encrypt_block(M, flipped), encrypt_block(M, K))

    def test_complementation_property(self):
        def complement(value):
            return "".join("1" if b == "0" else "0" for b in value)
        self.assertEqual(encrypt_block(complement(M), complement(K)), complement(encrypt_block(M, K)))

    def test_weak_key_is_its_own_inverse(self):
        weak = hex_to_bits("0101010101010101")
        self.assertEqual(encrypt_block(encrypt_block(M, weak), weak), M)

    def test_round_trip_on_random_blocks(self):
        rng = random.Random(4)
        for _ in range(100):
            block = format(rng.getrandbits(64), "064b")
            key = format(rng.getrandbits(64), "064b")
            self.assertEqual(decrypt_block(encrypt_block(block, key), key), block)

    def test_rejects_wrong_sizes(self):
        with self.assertRaises(ValueError):
            run_block("0" * 63, K)


if __name__ == "__main__":
    unittest.main()
