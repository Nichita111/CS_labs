"""The Playfair cipher on a rectangular matrix of any alphabet."""

from dataclasses import dataclass

from alphabet import ROMANIAN_ALPHABET

# 31 is prime, so no rectangle holds the Romanian alphabet exactly. A 4 x 8 matrix
# keeps all 31 letters and leaves one free cell, which holds a symbol.
ROWS, COLUMNS = 4, 8
FILLER = "*"
# The rarest Romanian letters (Table 2.1 of lab 2: Q 0.00%, W 0.03%).
SEPARATORS = ("Q", "W")


def build_matrix(key, alphabet=ROMANIAN_ALPHABET, rows=ROWS, columns=COLUMNS, filler=FILLER):
    """Key letters first (each kept only once), then the rest of the alphabet by rows."""
    cells = []
    for letter in list(key) + list(alphabet):
        if letter not in cells:
            cells.append(letter)
    free_cells = rows * columns - len(cells)
    if free_cells < 0:
        raise ValueError(f"a {rows} x {columns} matrix cannot hold {len(cells)} letters")
    cells.extend(filler * free_cells)
    return tuple(tuple(cells[row * columns:(row + 1) * columns]) for row in range(rows))


def split_into_pairs(text, separators=SEPARATORS, padding=None):
    """Cut the text into pairs of different letters.

    A separator goes between the two letters of a double, and the next double in a
    row gets the other separator: SSS gives SX SZ S.. in the lab's example. A last
    letter left alone is completed with `padding`, by default the separator that
    differs from it.
    """
    pairs = []
    position = 0
    last_inserted = None
    while position < len(text):
        first = text[position]
        second = text[position + 1] if position + 1 < len(text) else None
        if second is None:
            pairs.append(first + (padding or _other_than(first, separators)))
            position += 1
        elif first == second:
            inserted = _other_than(first, separators, avoid=last_inserted)
            pairs.append(first + inserted)
            last_inserted = inserted
            position += 1
        else:
            pairs.append(first + second)
            last_inserted = None
            position += 2
    return pairs


def _other_than(letter, separators, avoid=None):
    for separator in separators:
        if separator != letter and separator != avoid:
            return separator
    return separators[0] if separators[0] != letter else separators[1]


def _positions(matrix):
    return {cell: (row, column)
            for row, cells in enumerate(matrix)
            for column, cell in enumerate(cells)}


def _transform_pairs(pairs, matrix, step):
    """step = +1 encrypts and step = -1 decrypts; the rectangle rule is its own inverse."""
    position = _positions(matrix)
    rows, columns = len(matrix), len(matrix[0])
    result = []
    for first, second in pairs:
        row_1, column_1 = position[first]
        row_2, column_2 = position[second]
        if row_1 == row_2:
            result.append(matrix[row_1][(column_1 + step) % columns]
                          + matrix[row_2][(column_2 + step) % columns])
        elif column_1 == column_2:
            result.append(matrix[(row_1 + step) % rows][column_1]
                          + matrix[(row_2 + step) % rows][column_2])
        else:
            result.append(matrix[row_1][column_2] + matrix[row_2][column_1])
    return result


def encrypt_pairs(pairs, matrix):
    return _transform_pairs(pairs, matrix, +1)


def decrypt_pairs(pairs, matrix):
    return _transform_pairs(pairs, matrix, -1)


@dataclass(frozen=True)
class Encrypted:
    pairs: tuple
    ciphertext: str


def encrypt(text, key):
    """Encrypt prepared text; also returns the pairs, with inserted letters visible."""
    matrix = build_matrix(key)
    pairs = split_into_pairs(text)
    return Encrypted(tuple(pairs), "".join(encrypt_pairs(pairs, matrix)))


def decrypt(ciphertext, key):
    """Decrypt prepared ciphertext. Inserted letters and spaces are restored by hand."""
    matrix = build_matrix(key)
    pairs = [ciphertext[i:i + 2] for i in range(0, len(ciphertext), 2)]
    plaintext = "".join(decrypt_pairs(pairs, matrix))
    if FILLER in plaintext:
        raise ValueError(f"this text cannot come from this key: the symbol {FILLER} "
                         "never appears in a message.")
    return plaintext
