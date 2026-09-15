# noita-eye-puzzle

Statistical fingerprinting of the unsolved Noita eye-glyph cipher. Instead of guessing keys,
this project enciphers real text with candidate cipher machines and compares the resulting
statistics with the nine eye messages. It did not solve the puzzle. It did establish several
constraints that any solution must satisfy and excluded several mechanism families,
including the cut-based deck ciphers that had been the leading candidate.

Read **[FINDINGS.md](FINDINGS.md)** for the results. Highlights:

- Same-position coincidence between unrelated messages is exactly chance: a reused keystream
  over letters is excluded.
- Cut-based (rotating) deck ciphers are excluded: after East 4 and East 5 diverge they
  re-match at 55% for twenty positions, and every rotating mechanism re-matches at 0%.
- Isomorph bijections are never affine mod 83 and never act digit-wise on the base-5 eyes.
- The community's distance-4 significance (z = 4.04) double-counts shared prefixes; the
  deduplicated value is z = 3.65. The tail claims at distances 9 and 17 do not survive.
- The first symbol of each message is outside the cipher.
- A non-rotating deck that moves one card per letter is the only shape not excluded.

## Layout

- `data/` the community trigram transcription (see `data/SOURCES.md` for attribution)
- `harness/structure.py` every model-free number in FINDINGS.md section 2
- `harness/mech*.py`, `resync.py`, `robust.py`, `refine.py`, `joint.py` mechanism families
  and the two fingerprint scorers
- `results/` outputs of every run cited in FINDINGS.md

## Reproduce

Python 3, no third-party packages.

```
cd harness
python3 structure.py                 # section 2 numbers, seconds
sh fetch_corpus.sh                   # English/Finnish plaintext from GITenberg mirrors
python3 mech2.py en nospace          # first family, distance-curve score (~4 min)
python3 resync.py en nospace         # re-match fingerprint
python3 joint.py en nospace          # both fingerprints together (reads ../results/rs_*.txt)
python3 robust.py en nospace         # key-stability of the surviving family
python3 mech3.py en nospace          # second family
python3 mech4.py en nospace          # two-deck family
python3 mech5.py en nospace          # conditional-alphabet family (small-state bound)
```

Each script takes a language (`en`, `fi`) and `space` or `nospace` for whether the plaintext
keeps word spaces.

## Credits

Trigram transcription and the orthodox reading order are the work of the Noita eye-message
community (see the [Unsolved Puzzles page](https://unsolved-puzzles.github.io/unsolved-puzzles/noita/eye-puzzle.html)
and the repositories by ngraham20 and SirCapybar). Analysis and harness by trapperl with
Claude Code.
