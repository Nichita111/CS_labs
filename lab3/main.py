"""Interactive console program for Laboratory Work No. 3 (Playfair cipher)."""

import os
import sys

from playfair import COLUMNS, ROWS, SEPARATORS, build_matrix, decrypt, encrypt
from validation import MIN_KEY_LENGTH, parse_ciphertext, parse_key, parse_message

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
LABEL_WIDTH = 17  # the longest label: "key (≥ 7 letters)"
INDENT = "  "


def _paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(text):
    return _paint(text, "1")


def dim(text):
    return _paint(text, "2")


def red(text):
    return _paint(text, "31")


def green(text):
    return _paint(text, "1;32")


def cyan(text):
    return _paint(text, "36")


def menu():
    return "\n".join([
        bold("Playfair cipher · Romanian alphabet (n = 31)"),
        "",
        "  1  Encrypt a message",
        "  2  Decrypt a cryptogram",
        "  0  Exit",
        "",
    ])


def ask(label, parser, indent=INDENT, width=LABEL_WIDTH):
    """Ask until `parser` accepts the input; show its error message otherwise."""
    prompt = f"{indent}{label.ljust(width)} {cyan('›')} "
    while True:
        raw = input(prompt)
        try:
            return parser(raw)
        except ValueError as exc:
            print(red(f"{INDENT}✗ {exc} Try again."))


def show(label, value):
    """A label/value line aligned with the answers typed after "›"."""
    print(f"{INDENT}{label.ljust(LABEL_WIDTH)}   {value}")


def parse_menu_option(raw):
    option = raw.strip()
    if option not in ("0", "1", "2"):
        raise ValueError(f"invalid option {option!r}; choose 1, 2 or 0.")
    return option


def in_pairs(text):
    return " ".join(text[i:i + 2] for i in range(0, len(text), 2))


def ask_key_and_show_matrix():
    key = ask(f"key (≥ {MIN_KEY_LENGTH} letters)", parse_key)
    print()
    print(f"{INDENT}{dim(f'matrix {ROWS} x {COLUMNS}')}")
    for row in build_matrix(key):
        print(INDENT + INDENT + " ".join(f"{cell:>2}" for cell in row))
    print()
    return key


def task_encrypt():
    print(bold("Encrypt"))
    key = ask_key_and_show_matrix()
    message = ask("message", parse_message)
    result = encrypt(message, key)
    show("prepared", dim(message))
    show("pairs", dim(" ".join(result.pairs)))
    show("ciphertext", green(result.ciphertext))


def task_decrypt():
    print(bold("Decrypt"))
    key = ask_key_and_show_matrix()

    def parse_and_decrypt(raw):
        ciphertext = parse_ciphertext(raw)
        return ciphertext, decrypt(ciphertext, key)

    ciphertext, plaintext = ask("ciphertext", parse_and_decrypt)
    show("pairs", dim(in_pairs(ciphertext)))
    show("decrypted pairs", dim(in_pairs(plaintext)))
    show("plaintext", green(plaintext))
    print(dim(f"{INDENT}Spaces and the inserted {SEPARATORS[0]}/{SEPARATORS[1]} "
              "are restored by hand, from the meaning of the message."))


def main():
    tasks = {"1": task_encrypt, "2": task_decrypt}
    try:
        while True:
            print(menu())
            option = ask("option", parse_menu_option, indent="", width=0)
            if option == "0":
                print("bye")
                return
            print()
            tasks[option]()
            print()
    except (EOFError, KeyboardInterrupt):
        print("\nbye")


if __name__ == "__main__":
    main()
