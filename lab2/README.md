# Lab 2 · Cryptanalysis of Monoalphabetic Ciphers

Breaking variant 19 with frequency analysis, step by step. Python 3; only `make_chart.py` needs matplotlib. The report is in [REPORT.md](REPORT.md).

The ciphertext and the lab's PDF are course material and aren't in the repository, so create the local copy first (macOS):

```
python3 extract_variant.py "<path to the lab 2 PDF>" 19
python3 attack.py --stats --stages --key --check
python3 attack.py --full
python3 -m unittest discover tests -v
```

Without the local copy, the tests that need the ciphertext are skipped.
