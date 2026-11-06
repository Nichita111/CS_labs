# Lab 1 · Caesar Cipher (Romanian alphabet)

The Caesar cipher (Task 1.1) and the Caesar cipher with a keyword-permuted alphabet (Task 1.2) over the 31-letter Romanian alphabet. Python 3, standard library only. The report is in [REPORT.md](REPORT.md).

```
python3 main.py                          # interactive program
python3 -m unittest discover tests -v    # 42 unit tests
./scripts/take_screenshots.sh            # regenerates images/ (macOS, Terminal.app)
```

| File | Contents |
|---|---|
| `alphabet.py` | the alphabet (A = 0 … Z = 30), case conversion, text preparation |
| `cipher.py` | encrypt / decrypt, permuted alphabet, brute force |
| `validation.py` | key, text and keyword validation |
| `main.py` | console menu |
| `scripts/` | `take_screenshots.sh`, `play.exp` (replays a scenario), `scenarios/*.txt` (inputs) |
