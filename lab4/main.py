"""Interactive console program for Laboratory Work No. 4, task 2.8:
R(k) of DES from L(k-1) and the output of the S-boxes."""

import os
import random
import sys

from des import bits_to_hex, chunks, run_block, text_to_bits
from des_tables import P
from task import compute_right
from validation import (
    BLOCK_HINT,
    parse_block_text,
    parse_half_block,
    parse_menu_option,
    parse_round,
)

if os.name == "nt":
    os.system("")  # turns on ANSI colours in the classic Windows console
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
LABEL_WIDTH = 17  # the longest label: "message (8 chars)"
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
        bold("DES · task 2.8: R(k) from L(k-1) and S1(B1)...S8(B8)"),
        "",
        "  1  Enter L(k-1) and the S-box output",
        "  2  Generate them at random",
        "  3  Take them from a real DES encryption",
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


def show(label, value, width=LABEL_WIDTH):
    """A label/value line aligned with the answers typed after "›"."""
    print(f"{INDENT}{label.ljust(width)}   {value}")


def nibbles(bits):
    """Bits in groups of 4, the way the lab writes them."""
    return " ".join(chunks(bits, 4))


def heading(text):
    print()
    print(f"{INDENT}{bold(text)}")


def print_table(table, width=8):
    for start in range(0, len(table), width):
        print(INDENT * 3 + "".join(f"{p:>4}" for p in table[start:start + width]))


def show_solution(solution):
    """All the steps of task 2.8, from the given values to R(k)."""
    k = solution.round
    left_name, right_name = f"L{k - 1}", f"R{k}"

    heading("Table P  (bit i of f is bit P[i] of S1(B1)...S8(B8))")
    print_table(P)

    heading("Step 1. The S-box output, by box")
    print(INDENT * 3 + " ".join(f"{f'S{j}':^4}" for j in range(1, 9)))
    print(INDENT * 3 + " ".join(solution.s_groups) + dim(f"   = {bits_to_hex(solution.s_output)}"))

    heading("Step 2. f = P(S1(B1)...S8(B8))")
    for row, (positions, taken, _) in enumerate(solution.p_rows()):
        first = row * 8 + 1
        print(INDENT * 3 + dim(f"f[{first:>2}..{first + 7:>2}]") + "  bits "
              + " ".join(f"{p:>2}" for p in positions) + "  →  " + " ".join(taken))
    print(INDENT * 3 + f"{'f':<5}" + nibbles(solution.f) + dim(f"   = {bits_to_hex(solution.f)}"))

    heading(f"Step 3. {right_name} = {left_name} ⊕ f")
    width = max(len(left_name), len(right_name), 1)
    rows = (("  ", left_name, solution.left_prev),
            ("⊕ ", "f", solution.f),
            ("= ", right_name, solution.right))
    for sign, name, bits in rows:
        line = f"{sign}{name:<{width}}  {nibbles(bits)}   {bits_to_hex(bits)}"
        print(INDENT * 2 + (green(line) if name == right_name else line))
    print()
    show(right_name, green(f"{bits_to_hex(solution.right)}  ({nibbles(solution.right)})"))


def task_manual():
    print(bold("Enter the data"))
    print(dim(f"{INDENT}32-bit values: {BLOCK_HINT}"))
    k = ask("round k (1-16)", parse_round)
    left = ask(f"L{k - 1}", parse_half_block)
    s_output = ask("S1(B1)...S8(B8)", parse_half_block)
    show_solution(compute_right(k, left, s_output))


def task_random(rng=random):
    print(bold("Random data"))
    k = rng.randint(1, 16)
    left = format(rng.getrandbits(32), "032b")
    s_output = format(rng.getrandbits(32), "032b")
    show("round k", k)
    show(f"L{k - 1}", f"{bits_to_hex(left)}  ({nibbles(left)})")
    show("S1(B1)...S8(B8)", f"{bits_to_hex(s_output)}  ({nibbles(s_output)})")
    show_solution(compute_right(k, left, s_output))


def task_from_des():
    """Run real DES up to round k, hand L(k-1) and the S-box output to the task, compare R(k)."""
    print(bold("From a real DES encryption"))
    message = ask("message (8 chars)", parse_block_text)
    key = ask("key (8 chars)", parse_block_text)
    k = ask("round k (1-16)", parse_round)
    trace = run_block(text_to_bits(message), text_to_bits(key))
    schedule = trace.schedule

    heading("DES up to round k")
    show("M (ASCII)", " ".join(f"{ord(c):02X}" for c in message) + dim(f"   = {bits_to_hex(trace.block)}"))
    show("K (ASCII)", " ".join(f"{ord(c):02X}" for c in key) + dim(f"   = {bits_to_hex(schedule.key)}"))
    show("K+ = PC1(K)", " ".join(chunks(schedule.k_plus, 7)))
    show(f"C{k}  D{k}", " ".join(chunks(schedule.c[k], 7)) + "   " + " ".join(chunks(schedule.d[k], 7)))
    show("IP(M) = L0 R0", f"{bits_to_hex(trace.permuted[:32])} {bits_to_hex(trace.permuted[32:])}")
    for step in trace.rounds[:k - 1]:
        show(f"round {step.number}", f"L{step.number} = {bits_to_hex(step.left)}   "
                                     f"R{step.number} = {bits_to_hex(step.right)}")

    current = trace.rounds[k - 1]
    heading(f"Round {k}, up to the S-boxes")
    show(f"K{k} = PC2(C{k}D{k})", " ".join(chunks(current.subkey, 6)))
    show(f"E(R{k - 1})", " ".join(chunks(current.expanded, 6)))
    show(f"B = K{k} ⊕ E(R{k - 1})", " ".join(chunks(current.mixed, 6)))
    for step in current.s_steps:
        show(f"S{step.box}(B{step.box})", f"{step.six_bits}: row {step.row}, column {step.column:>2} "
                                          f"→ {step.value:>2} = {step.four_bits}")

    print()
    show("given L" + str(k - 1), f"{bits_to_hex(current.left_in)}  ({nibbles(current.left_in)})")
    show("given S-output", f"{bits_to_hex(current.s_output)}  ({nibbles(current.s_output)})")
    solution = compute_right(k, current.left_in, current.s_output)
    show_solution(solution)
    if solution.right == current.right:
        show("check", green(f"✓ the same R{k} as the full DES computation"))
    else:  # pragma: no cover - would mean a bug in task.py or des.py
        show("check", red(f"✗ DES computed R{k} = {bits_to_hex(current.right)}"))


def main():
    if hasattr(sys.stdout, "reconfigure") and (sys.stdout.encoding or "").lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    tasks = {"1": task_manual, "2": task_random, "3": task_from_des}
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
