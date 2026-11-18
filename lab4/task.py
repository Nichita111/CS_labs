"""Task 2.8: compute R(k) for round k of DES, knowing L(k-1) and the result
of the S-boxes, S1(B1)S2(B2)...S8(B8).

The round function is f(R(k-1), K(k)) = P(S1(B1)...S8(B8)), and
R(k) = L(k-1) XOR f. Once the S-boxes are done, only two steps are left:
the permutation P and the XOR with the left half."""

from dataclasses import dataclass

from des import chunks, permute, xor
from des_tables import P

HALF = 32


@dataclass(frozen=True)
class Solution:
    round: int
    left_prev: str    # L(k-1)
    s_output: str     # S1(B1)..S8(B8)
    f: str            # P(S1(B1)..S8(B8))
    right: str        # R(k) = L(k-1) XOR f

    @property
    def s_groups(self):
        """The S-box output split into S1(B1), ..., S8(B8), 4 bits each."""
        return chunks(self.s_output, 4)

    def p_rows(self, width=8):
        """P in rows of `width`: (positions, the bits taken from the S-box output, f's bits)."""
        rows = []
        for start in range(0, HALF, width):
            positions = P[start:start + width]
            taken = "".join(self.s_output[p - 1] for p in positions)
            rows.append((positions, taken, self.f[start:start + width]))
        return rows


def compute_right(round_number, left_prev, s_output):
    """R(k) = L(k-1) XOR P(S1(B1)...S8(B8))."""
    if not 1 <= round_number <= 16:
        raise ValueError("DES has rounds 1 to 16")
    for name, bits in (("L(k-1)", left_prev), ("the S-box output", s_output)):
        if len(bits) != HALF or set(bits) - {"0", "1"}:
            raise ValueError(f"{name} must be {HALF} bits")
    f = permute(s_output, P)
    return Solution(round_number, left_prev, s_output, f, xor(left_prev, f))
