# Lab 4 · Block Ciphers: DES

Task 2.8 (19 mod 11 = 8): compute R(k) of a DES round from L(k-1) and the S-box output S1(B1)...S8(B8). The program also contains the whole DES algorithm, so the result can be checked against a real encryption. Python 3, standard library only. The report is in [REPORT.md](REPORT.md).

```
python main.py                                # interactive program
python -m unittest discover tests -v          # unit tests
python scripts/render_screenshots.py          # regenerates images/ (Windows, needs Pillow)
```
