"""Save one ciphertext variant from the lab's PDF into data/V<n>.txt (macOS only).

    python3 extract_variant.py "<path to the lab 2 PDF>" 19

The ciphertexts are course material, so data/ is not in the repository.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

PDF_TEXT_SCRIPT = """
ObjC.import("PDFKit"); ObjC.import("stdlib");
$.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath($.getenv("PDF_PATH"))).string.js
"""


def pdf_text(path):
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", PDF_TEXT_SCRIPT],
        env={**os.environ, "PDF_PATH": str(path)},
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def variant_text(text, number):
    """The lines between the headings `V<number>` and `V<number + 1>`."""
    match = re.search(rf"^V{number}$\n(.*?)^(?:V{number + 1})?$\n?", text, re.M | re.S)
    if match is None:
        raise ValueError(f"variant V{number} not found")
    return match.group(1)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    number = int(sys.argv[2])
    target = Path(__file__).parent / "data" / f"V{number}.txt"
    target.parent.mkdir(exist_ok=True)
    target.write_text(variant_text(pdf_text(sys.argv[1]), number), encoding="utf-8")
    print(f"saved {target}")


if __name__ == "__main__":
    main()
