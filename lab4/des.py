"""The whole DES algorithm (FIPS 46-3), one 64-bit block at a time.

Blocks are strings of "0" and "1", so every intermediate value can be
printed exactly as the standard writes it. That is slow, but DES is only
used here to show and check the steps of one round."""

from dataclasses import dataclass

from des_tables import E, IP, IP_INVERSE, P, PC1, PC2, S_BOXES, SHIFTS

ROUNDS = 16


def permute(bits, table):
    """Output bit i is input bit table[i] (positions count from 1)."""
    return "".join(bits[position - 1] for position in table)


def xor(a, b):
    if len(a) != len(b):
        raise ValueError(f"cannot XOR {len(a)} bits with {len(b)} bits")
    return "".join("1" if x != y else "0" for x, y in zip(a, b))


def rotate_left(bits, count):
    return bits[count:] + bits[:count]


def chunks(bits, size):
    return [bits[i:i + size] for i in range(0, len(bits), size)]


def bits_to_hex(bits):
    return format(int(bits, 2), f"0{len(bits) // 4}X")


def hex_to_bits(text):
    return format(int(text, 16), f"0{len(text) * 4}b")


def text_to_bits(text):
    """8 ASCII characters -> 64 bits (8 bits per character, as in the ASCII table)."""
    if len(text) != 8 or any(ord(char) > 127 for char in text):
        raise ValueError("a DES block is exactly 8 ASCII characters")
    return "".join(format(ord(char), "08b") for char in text)


@dataclass(frozen=True)
class SBoxStep:
    """One S-box: the 6 bits B(j), the row (outer bits), the column (inner bits), the 4-bit result."""
    box: int
    six_bits: str
    row: int
    column: int
    value: int

    @property
    def four_bits(self):
        return format(self.value, "04b")


def s_box(box, six_bits):
    """S(j)(B(j)): the first and last bit choose the row, the middle four the column."""
    row = int(six_bits[0] + six_bits[5], 2)
    column = int(six_bits[1:5], 2)
    return SBoxStep(box, six_bits, row, column, S_BOXES[box - 1][row][column])


def s_boxes(bits48):
    """B1..B8 -> S1(B1)..S8(B8), 48 -> 32 bits."""
    steps = [s_box(box, six_bits) for box, six_bits in enumerate(chunks(bits48, 6), start=1)]
    return "".join(step.four_bits for step in steps), steps


@dataclass(frozen=True)
class KeySchedule:
    key: str          # the 64-bit key K
    k_plus: str       # K+ = PC1(K), 56 bits
    c: tuple          # C0..C16, 28 bits each
    d: tuple          # D0..D16, 28 bits each
    subkeys: tuple    # K1..K16, 48 bits each (subkeys[0] is K1)


def key_schedule(key):
    k_plus = permute(key, PC1)
    c, d = [k_plus[:28]], [k_plus[28:]]
    for shift in SHIFTS:
        c.append(rotate_left(c[-1], shift))
        d.append(rotate_left(d[-1], shift))
    subkeys = tuple(permute(c[i] + d[i], PC2) for i in range(1, ROUNDS + 1))
    return KeySchedule(key, k_plus, tuple(c), tuple(d), subkeys)


@dataclass(frozen=True)
class Round:
    number: int
    left_in: str      # L(i-1)
    right_in: str     # R(i-1)
    subkey: str       # K(i)
    expanded: str     # E(R(i-1))
    mixed: str        # K(i) XOR E(R(i-1)) = B1..B8
    s_output: str     # S1(B1)..S8(B8)
    s_steps: tuple
    f: str            # P(S1(B1)..S8(B8))
    left: str         # L(i) = R(i-1)
    right: str        # R(i) = L(i-1) XOR f


def feistel_round(number, left_in, right_in, subkey):
    expanded = permute(right_in, E)
    mixed = xor(subkey, expanded)
    s_output, s_steps = s_boxes(mixed)
    f = permute(s_output, P)
    return Round(number, left_in, right_in, subkey, expanded, mixed, s_output,
                 tuple(s_steps), f, right_in, xor(left_in, f))


@dataclass(frozen=True)
class BlockTrace:
    block: str
    schedule: KeySchedule
    permuted: str     # IP(block) = L0 R0
    rounds: tuple     # 16 Round objects
    preoutput: str    # R16 L16
    output: str       # IP^-1(R16 L16)


def run_block(block, key, decrypt=False):
    """Encrypt (or decrypt) one 64-bit block, keeping every intermediate value."""
    if len(block) != 64 or len(key) != 64:
        raise ValueError("DES works on 64-bit blocks with a 64-bit key")
    schedule = key_schedule(key)
    subkeys = schedule.subkeys[::-1] if decrypt else schedule.subkeys
    permuted = permute(block, IP)
    left, right = permuted[:32], permuted[32:]
    rounds = []
    for number, subkey in enumerate(subkeys, start=1):
        step = feistel_round(number, left, right, subkey)
        rounds.append(step)
        left, right = step.left, step.right
    preoutput = right + left  # the halves are swapped after round 16
    return BlockTrace(block, schedule, permuted, tuple(rounds), preoutput,
                      permute(preoutput, IP_INVERSE))


def encrypt_block(block, key):
    return run_block(block, key).output


def decrypt_block(block, key):
    return run_block(block, key, decrypt=True).output
