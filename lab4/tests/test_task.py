import random
import unittest

from des import bits_to_hex, hex_to_bits, permute, run_block, xor
from des_tables import E, P
from task import compute_right


class TestComputeRight(unittest.TestCase):
    def test_grabbe_round_1(self):
        # L0 = CC00CCFF and S1(B1)..S8(B8) = 5C82B597 give f = 234AA9BB and R1 = EF4A6544.
        solution = compute_right(1, hex_to_bits("CC00CCFF"), hex_to_bits("5C82B597"))
        self.assertEqual(bits_to_hex(solution.f), "234AA9BB")
        self.assertEqual(bits_to_hex(solution.right), "EF4A6544")
        self.assertEqual(solution.s_groups, ["0101", "1100", "1000", "0010",
                                             "1011", "0101", "1001", "0111"])

    def test_matches_every_round_of_real_des(self):
        """Given only L(k-1) and the S-box output of a real run, the task finds DES's own R(k)."""
        rng = random.Random(19)
        for _ in range(30):
            trace = run_block(format(rng.getrandbits(64), "064b"), format(rng.getrandbits(64), "064b"))
            for step in trace.rounds:
                solution = compute_right(step.number, step.left_in, step.s_output)
                self.assertEqual(solution.f, step.f)
                self.assertEqual(solution.right, step.right)

    def test_each_s_box_bit_lands_where_p_says(self):
        for source in range(1, 33):
            s_output = "".join("1" if i == source else "0" for i in range(1, 33))
            f = compute_right(1, "0" * 32, s_output).f
            self.assertEqual(f.index("1") + 1, P.index(source) + 1)
            self.assertEqual(f.count("1"), 1)

    def test_each_s_box_reaches_six_other_boxes_of_the_next_round(self):
        """P, followed by the next round's E, sends S(j)'s 4 bits to 6 S-boxes, never to S(j)."""
        for box in range(1, 9):
            positions = {P.index(bit) + 1 for bit in range(4 * box - 3, 4 * box + 1)}
            reached = {i // 6 + 1 for i, bit in enumerate(E) if bit in positions}
            self.assertEqual(len(reached), 6)
            self.assertNotIn(box, reached)

    def test_zero_left_half_gives_f_itself(self):
        s_output = hex_to_bits("DAC18A4C")
        self.assertEqual(compute_right(5, "0" * 32, s_output).right, permute(s_output, P))

    def test_xor_with_l_can_be_undone(self):
        left, s_output = hex_to_bits("ACEAE4EC"), hex_to_bits("DAC18A4C")
        solution = compute_right(3, left, s_output)
        self.assertEqual(bits_to_hex(solution.right), "755365CE")
        self.assertEqual(xor(solution.right, solution.f), left)

    def test_p_rows_show_the_bits_taken(self):
        solution = compute_right(1, hex_to_bits("CC00CCFF"), hex_to_bits("5C82B597"))
        rows = solution.p_rows()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0], ((16, 7, 20, 21, 29, 12, 28, 17), "00100011", "00100011"))
        self.assertEqual("".join(taken for _, taken, _ in rows), solution.f)

    def test_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            compute_right(0, "0" * 32, "0" * 32)
        with self.assertRaises(ValueError):
            compute_right(17, "0" * 32, "0" * 32)
        with self.assertRaises(ValueError):
            compute_right(1, "0" * 31, "0" * 32)
        with self.assertRaises(ValueError):
            compute_right(1, "0" * 32, "2" * 32)


if __name__ == "__main__":
    unittest.main()
