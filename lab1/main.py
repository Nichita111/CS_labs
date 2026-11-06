"""Interactive console program for Laboratory Work No. 1 (Caesar cipher)."""

import os
import sys

from alphabet import N, ROMANIAN_ALPHABET
from cipher import (
    brute_force,
    build_permuted_alphabet,
    decrypt,
    decrypt_with_keyword,
    encrypt,
    encrypt_with_keyword,
)
from validation import MIN_KEYWORD_LENGTH, parse_key, parse_keyword, parse_text

MENU = f"""
==================================================
  Caesar cipher - Romanian alphabet (n = {N})
==================================================
  1 - Caesar cipher (Task 1.1)
  2 - Caesar cipher with permutation (Task 1.2)
  3 - Brute-force attack on the Caesar cipher
  0 - Exit"""

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def error(text):
    return _paint(text, "31")


def result(text):
    return _paint(text, "1;32")


def ask(prompt, parser):
    """Ask until `parser` accepts the input; show its error message otherwise."""
    while True:
        raw = input(prompt)
        try:
            return parser(raw)
        except ValueError as exc:
            print(error(f"  Error: {exc} Try again."))


def parse_menu_option(raw):
    option = raw.strip()
    if option not in ("0", "1", "2", "3"):
        raise ValueError(f"invalid option {option!r}; choose 1, 2, 3 or 0.")
    return option


def parse_operation(raw):
    operation = raw.strip().lower()
    if operation in ("e", "encrypt"):
        return "encrypt"
    if operation in ("d", "decrypt"):
        return "decrypt"
    raise ValueError(f"invalid operation {raw.strip()!r}; type E to encrypt or D to decrypt.")


def ask_operation():
    return ask("Operation - [E]ncrypt or [D]ecrypt: ", parse_operation)


def ask_key(label="Key"):
    return ask(f"{label} (integer from 1 to {N - 1}): ", parse_key)


def ask_text(operation):
    label = "Message" if operation == "encrypt" else "Ciphertext"
    text = ask(f"{label}: ", parse_text)
    print(f"Prepared text (uppercase, no spaces): {text}")
    return text


def print_result(operation, text):
    label = "Ciphertext" if operation == "encrypt" else "Decrypted message"
    print(result(f"{label}: {text}"))


def format_permutation_table(permuted, key):
    """Rows x / m / c as in Table 3 of the lab, split in two blocks."""
    n = len(permuted)
    lines = []
    for start in range(0, n, 16):
        positions = range(start, min(start + 16, n))
        lines.append("x " + "".join(f"{x:>3}" for x in positions))
        lines.append("m " + "".join(f"{permuted[x]:>3}" for x in positions))
        lines.append("c " + "".join(f"{permuted[(x + key) % n]:>3}" for x in positions))
        lines.append("")
    return "\n".join(lines)


def task_caesar():
    print("\n--- Caesar cipher (Task 1.1) ---")
    operation = ask_operation()
    key = ask_key()
    text = ask_text(operation)
    if operation == "encrypt":
        print_result(operation, encrypt(text, key))
    else:
        print_result(operation, decrypt(text, key))


def task_caesar_with_keyword():
    print("\n--- Caesar cipher with permutation (Task 1.2) ---")
    operation = ask_operation()
    key = ask_key("Key 1")
    keyword = ask(
        f"Key 2 (keyword, at least {MIN_KEYWORD_LENGTH} Romanian letters): ",
        parse_keyword,
    )
    permuted = build_permuted_alphabet(keyword)
    print(f"\nStandard alphabet: {''.join(ROMANIAN_ALPHABET)}")
    print(f"Permuted alphabet: {''.join(permuted)}\n")
    print(format_permutation_table(permuted, key))
    text = ask_text(operation)
    if operation == "encrypt":
        print_result(operation, encrypt_with_keyword(text, key, keyword))
    else:
        print_result(operation, decrypt_with_keyword(text, key, keyword))


def task_brute_force():
    print("\n--- Brute-force attack on the Caesar cipher ---")
    ciphertext = ask_text("decrypt")
    candidates = brute_force(ciphertext)
    half = (len(candidates) + 1) // 2
    for (k1, left), right in zip(candidates[:half], candidates[half:] + [None]):
        line = f"k={k1:>2}  {left}"
        if right is not None:
            k2, text = right
            line = f"{line:<{len(left) + 12}}k={k2:>2}  {text}"
        print(line)


def main():
    tasks = {"1": task_caesar, "2": task_caesar_with_keyword, "3": task_brute_force}
    try:
        while True:
            print(MENU)
            option = ask("Choose an option: ", parse_menu_option)
            if option == "0":
                print("Bye!")
                return
            tasks[option]()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")


if __name__ == "__main__":
    main()
