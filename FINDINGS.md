# Findings: statistical fingerprinting of the Noita eye-glyph cipher

Status: **unsolved**. This document records what one analysis session (September 2026)
established, what it ruled out, and what remains. Everything here is reproducible from the
scripts in `harness/`; every number below is printed by `harness/structure.py` or is in a
file under `results/`.

## 1. Data and conventions

Nine messages, 1036 trigram symbols in the alphabet 0..82, under the community's orthodox
reading order (the one of 36 that gives an unbroken 0..82 range). Positions are 1-based.
Message lengths: E1 99, W1 103, E2 118, W2 102, E3 137, W3 124, E4 119, W4 120, E5 114.

## 2. Structural facts (no model assumed)

**2.1 Flat symbol distribution.** Index of coincidence times 83 is 1.066 (1.0 = uniform).
Chi-square against uniform is 150 on 82 degrees of freedom. Counts range from 3 (symbol 27)
to 26 (symbol 5). This is far too flat for a monoalphabetic substitution of letters.

**2.2 Shared headers, and the first symbol is outside the cipher.** After a first symbol
that is unique to each message, E1/W1/E2 agree exactly on positions 2..25, E4/W4/E5 on
2..21, and all nine on 2..3. Twenty-four identical outputs following *different* first
symbols is impossible for any state machine whose state depends on the first symbol's
plaintext: every deck, autokey and Chaocipher-type machine simulated in section 4 diverges
immediately after a changed letter. The first symbol is therefore a plain header (a message
number, presumably) and the cipher proper starts at position 2 from a common initial state.

**2.3 Diverged siblings re-match.** E1 and W1 differ at 26..29, agree at 30..33, differ at
34..37, agree at 38..49, then diverge. E4 and E5 differ at 22..25 and then re-match at 26,
27, 28, 30, 31, 32, 36, 39, 40, 41, 43: 11 of the next 20 positions (55%), decaying to
chance after about position 45. W4 against either re-matches at chance. Re-match profile in
10-position bins from the divergence point:

| pair | bin 1 | bin 2 | bin 3 | bin 4 |
|---|---|---|---|---|
| E4/E5 | 5/10 | 5/10 | 1/10 | 0/10 |
| E1/W1 | 4/10 | 8/10 | 5/10 | 1/10 |
| W4/E5 | 1/10 | 0/10 | 0/10 | 2/10 |
| E4/W4 | 1/10 | 0/10 | 0/10 | 0/10 |

**2.4 Unrelated messages coincide at chance.** Over all message pairs that share no
plaintext, same-position coincidences from position 27 on: 31 of 2459 (0.0126) against a
chance rate of 0.0120. A reused position-keyed keystream over letter plaintext would give
about 160 (the plaintext index of coincidence, ~0.065). **A many-time pad over letters is
excluded.**

**2.5 No repeats at distance 1, excess at distance 4.** Distance-d repeat counts, raw and
with shared regions deduplicated (a pair (t, t+d) in a later message is dropped if an
earlier message has the identical symbols at the same positions). Expected counts assume
uniform 1/83.

| d | raw obs / exp | z | dedup obs / exp | z |
|---|---|---|---|---|
| 1 | 0 / 12.4 | -3.54 | 0 / 10.9 | **-3.32** |
| 2 | 5 / 12.3 | -2.09 | 5 / 11.0 | -1.81 |
| 3 | 9 / 12.2 | -0.91 | 8 / 11.0 | -0.91 |
| 4 | 26 / 12.0 | +4.04 | 23 / 11.0 | **+3.65** |
| 9 | 18 / 11.5 | +1.93 | 16 / 10.8 | +1.58 |
| 13 | 19 / 11.1 | +2.40 | 19 / 10.6 | +2.58 |
| 15 | 4 / 10.9 | -2.09 | 4 / 10.5 | -2.02 |
| 17 | 18 / 10.6 | +2.27 | 14 / 10.4 | +1.12 |
| 19 | 3 / 10.4 | -2.31 | 3 / 10.3 | -2.28 |
| 22 | 3 / 10.1 | -2.25 | 3 / 10.0 | -2.24 |

All other distances up to 24 are within 1.7 sigma. The community's published distance-4
figure (z = 4.04) is the raw one and double-counts the shared prefixes (e.g. E4, W4 and E5
all contribute the same pair at position 7). Deduplicated it is z = 3.65, still real. The
apparent bumps at 9 and 17 mostly disappear after deduplication; 13 survives at 2.6 sigma;
the deficits at 15, 19 and 22 are each about 2 sigma. With 24 distances tested, the tail
beyond 4 should be treated as marginal.

The distance-4 pairs are not a layout artefact: 4 of 26 straddle a 26-trigram row-pair
boundary, exactly the 4.0 expected, and their positions within rows are unremarkable.

**2.6 No repeated n-grams except at aligned positions.** No 3-gram recurs anywhere in the
corpus except at identical positions within the related pairs above. A letter-level
substitution of 1036 characters of natural language would show dozens of repeated trigrams.

**2.7 Isomorphs and what their bijections are not.** Taking 10-symbol windows with at least
two internal repeats, 73 window pairs share a repeat pattern at different places (the
community's "Lymm patterns"; e.g. E1 at 41 and 69, W1 at 41 and 71, E2 at 46 and 81 all
carry pattern ABCDECFAEG). Under an isomorphic (group-autokey) cipher the two ciphertexts of
a repeated phrase are related by a fixed bijection. Of the 70 non-identical pairs, **0 are
affine mod 83** (x -> ax+b) and **0 are digit-wise consistent** (digit i of the image
depending only on digit i of the source, over the base-5 eye digits). Random bijections are
digit-wise consistent at rate 0.0 too, so the digit test has full power. Consequences: the
affine group AGL(1,83), which the community had left open, is excluded as the group of an
isomorphic cipher; and the three base-5 eye digits of a trigram carry no separable meaning,
so the trigram value is an opaque label.

**2.8 Cyclic homophonic substitution excluded.** If each letter cycled through a fixed list
of homophones, then between two consecutive uses of a symbol every other homophone of the
same letter would occur exactly once. Testing every symbol with at least four such
intervals (58 symbols) finds only three weak, non-mutual candidate pairs, consistent with
chance. Symbols also recur at gaps as short as 2.

## 3. What section 2 already implies

- The cipher is position-independent and stateful: identical plaintext from an identical
  state gives identical ciphertext (2.2), unrelated plaintext gives chance coincidence
  (2.4), and a perturbation to the state partly heals (2.3).
- The state perturbation caused by one changed letter is small: after a 4-letter change,
  about half of the next 20 outputs are unaffected (2.3).
- The machine never emits the same symbol twice in a row (2.5). Whatever it does after each
  output always moves the just-used symbol out of reach for one step.
- Something about it favours a symbol coming back exactly four steps later (2.5).

## 4. Mechanism simulation

**Method.** Rather than attack keys, encipher real English (Sherlock Holmes, Alice) and
Finnish (Kalevala) text with candidate machines under random keys and compare the resulting
statistics to the eye data. Two fingerprints: (a) the distance-d repeat curve, scored as a
Poisson deviance of the observed eye counts against the machine's expected ratios, and (b)
the re-match rate over the 20 positions after a 4-letter plaintext change (target 0.55).
Fingerprint (a) is a property of the mechanism, independent of key and text, only when it
is stable across random keys; the robustness sweep (`results/rb_*.txt`) checks that.

**Families tested** (about 1500 variants, `harness/mech.py`, `mech2.py`, `mech3.py`, `mech4.py`, `mech5.py`):

- Lookup decks: output the card at a fixed per-letter slot, then move that card (to a fixed
  depth, to a relative depth, by swap, with or without a cut of the deck to the output
  position, with a constant rotation, with a letter-dependent depth, with a moving
  insertion point, with a second card move). Slot layouts: contiguous, spaced by 2/3/4,
  random.
- Cut decks: rotate the deck by a per-letter amount, output the top, bury it.
- Chaocipher generalised to 83 cells with a homophonic plaintext disk; equal and unequal
  nadirs; ciphertext-disk-only variants.
- Two-deck machines: a keyed letter deck and a keyed symbol deck, output the symbol at the
  letter's index, then move the letter (to back, front, a depth, a swap, a rotation) and the
  symbol (to a depth, relative depth, swap, back, front); also with a homophonic letter deck.
- Conditional alphabets: m substitution alphabets selected by the class of the previous
  ciphertext symbol or previous plaintext letter, with alphabets drawing from any symbol,
  excluding their own class (no doubles by design), or from the next class in a ring.
- Controls: position-keyed random substitution, random group autokey over S83, additive
  ciphertext-feedback streams.

**Results.**

| family | distance curve | re-match after 4-letter change | verdict |
|---|---|---|---|
| position-keyed / random GAK / streams | flat (no distance-1 zero, no distance-4 peak) | 0.01 | excluded |
| cut-based decks (cut to output, bury at depth k) | best fit of all (deviance 6-7 on d=1..8, vs 43 for flat) | **0.00-0.01** | excluded by re-match |
| Chaocipher, nadir mid-deck | poor | 0.03-0.14 | excluded |
| Chaocipher, nadir 4 | poor | 0.35 -> 0.21 | excluded on curve |
| local swap (swap output with card k away) | produces doubles (d1 = 0.13-0.28) | 0.68-0.70 | excluded by no-doubles |
| non-rotating move-to-depth k, structured slots | stable across keys, but d1..d6 never matches | 0.31-0.37 | excluded on curve |
| non-rotating move-to-depth k, random slots | can match perfectly, but the curve depends on the slot layout: d4 ratio ranges 0.0-5.5 across keys | 0.33-0.35 | not excluded, not supported |
| rotation-plus-move, two-move, letter-depth, moving nadir | never both | <= 0.33 | excluded |
| two-deck (letter deck + symbol deck, same index, each deck moved by a simple rule) | best stable variants have no distance-4 peak (d4 = 0.85) | 0.33-0.35 | excluded on curve |
| conditional alphabets (previous ciphertext or plaintext class selects one of m alphabets, m = 2..10) | uniformly elevated at every distance (1.3-2.5), no peak | 0.54-0.96 | excluded on curve |

The conditional-alphabet result gives a quantitative bound. With m alphabets the ciphertext
repeat ratio at every distance is roughly 83 x (plaintext letter coincidence, ~0.065) / m,
which is 1.3 even at m = 10. The eye data sit at 1.00 +/- 0.1 for distances 5 to 8, so the
plaintext letter statistics are fully hidden there: the machine's effective number of
distinguishable states is at least about 50, and no small-state polyalphabetic (rotor
stepping, ciphertext-selected or plaintext-selected alphabets, short-period keys) can
produce the data. The community's "hidden state far exceeds 83" claim is confirmed by this
independent route.

The cut-based result is the sharpest: any mechanism that rotates the deck by a
plaintext-dependent amount leaves the two sibling decks rotated relative to each other after
a divergence, so they never re-match. The E4/E5 data therefore require a **non-rotating**
mechanism, or one whose rotation is plaintext-independent.

The one family that is not excluded, a non-rotating deck where the card at the letter's slot
is output and reinserted at a fixed depth, robustly reproduces the re-match rate (0.33-0.35
for a 4-letter change, 0.57-0.66 for a 1-letter change, across every depth and slot layout
tried) and produces the no-doubles property for most depths, but its distance curve is
governed by the slot layout, which is a key parameter, not a mechanism property. A
particular random layout fit the eye curve to deviance 6 on 8 degrees of freedom; others fit
nothing. The real machine, if it is in this family, has a structured layout that was not
among the ones tried (contiguous, spaced by 2, 3 or 4).

### 4.1 Exhaustive slot-layout sweep of the surviving family

To settle whether a structured slot layout rescues the non-rotating move-to-depth deck, a C
implementation (`harness/sweep.c`) enumerated every arithmetic-progression layout: slot of
letter j = (a + s * rank(j)) mod 83 with offset a in 0..82, spacing s in 1..41, rank either
alphabetical or by corpus frequency, and every insertion depth k in 0..82. That is 564,898
configurations per language, each run with three random decks over 12,000 symbols of text
(English without spaces; Finnish with spaces). Selection statistic: Poisson deviance of the
eye counts at distances 1..8 against the configuration's mean curve, with the spread of the
distance-4 ratio across decks as a stability check (`results/sweep_*_top.txt`).

With half a million trials the best deviances (2.4 English, 4.3 Finnish, on 8 degrees of
freedom) are what chance produces, so the top 300 stable configurations per language were
re-scored on statistics they were not selected on (`harness/sweep_verify.py`,
`results/sweepv_*.txt`): re-match after a 4-letter change, index of coincidence, and the
distance tail 9..24 against the deduplicated target.

Result: every one of the 600 configurations re-matches at 0.29-0.40 after a 4-letter change
(target 0.55; distribution: 421 at ~0.3, 178 at ~0.4, 1 at 0.2). The tail deviance is the
same as a flat curve for all of them, so it neither helps nor hurts. **The re-match rate of
this family is a property of the mechanism, capped near 0.4 for a 4-letter change, and no
layout changes it.** The family survives only if East 4 and East 5 differ by fewer than four
letters in positions 22..25 (a one-letter change re-matches at 0.57-0.66 in this family),
which the ciphertext alone cannot decide: all three of E4, W4, E5 differ pairwise at 22, 24
and 25, with single coincidences at 23 (W4/E5) and 25 (E4/W4).

Layouts and depths that fit the distance curve in both languages cluster at spacings 4, 10,
18, 38 and 40, but with no re-match discrimination this is not evidence of anything.

### 4.2 Correction: the re-match cap does not exclude the family

The 0.55 target treated the E4/E5 rate as a mean the mechanism must reach. It is a single
observation, so the right question is how often the mechanism produces it. Simulating the
60 best configurations per language (`harness/perturb.py`, 60 trials each):

| change | window | mean matches | P(as many as observed) |
|---|---|---|---|
| 1 letter | next 23 | 14.0 (fi), 14.4 (en) | E1/W1 has 16: **0.48 / 0.50** |
| 2 letters | next 23 | 10.7 / 10.6 | 16: 0.23 / 0.22 |
| 4 letters | next 20 | 6.8 / 6.9 | E4/E5 has 11: **0.21 / 0.19** |

So E1/W1 is the median outcome of a one-letter change and E4/E5 is an upper-quintile
outcome of a four-letter change. The family reproduces both, and the earlier statement that
its re-match rate is "capped" was the wrong test. The reading this implies: **East 1 and
West 1 are the same text through position 50 except for one letter at 26** (the differing
symbols at 27-29 and 34-37 are perturbation, not a second differing word), and **East 4 and
East 5 share their text through about position 45 except for a four-letter field at
22-25**. In this family a one-letter change perturbs exactly the letters whose slots lie
between the two changed letters' slots, so the E1/W1 pattern says the letters at 27, 28,
29, 34, 35, 36, 37 have slots inside that interval and the letters at 30-33 and 38-49
outside it.

The family therefore stands as the one candidate consistent with every measurement:
no doubles, distance-4 excess, flat tail, chance coincidence between unrelated messages,
and both re-match patterns. It is still only a candidate: its curve fit is unremarkable
given the number of layouts tried, and nothing yet ties a specific layout or depth to the
data. The decisive test is a key search under the mechanism, which is a constraint problem
(decrypting under a candidate initial deck must visit only slot positions, for all nine
messages from one initial deck), not an n-gram hill-climb.

### 4.3 Key-search feasibility

`harness/cpsat_search.py` encodes the decisive test for the surviving family as a CP-SAT
model (OR-tools): one integer position per card per time step, reified shift constraints
for the pop-and-insert move, a shared initial deck across messages, and the constraint that
every decryption step lands on one of at most 30 slot positions. On synthetic Finnish
ciphertext with a known key: a single 60-symbol message solves in 27 s but is
underdetermined (a spurious key satisfies it); three 100-symbol messages do not solve in
600 s on 4 cores. The real instance is 1,027 steps across nine messages, so this encoding
is not viable. A workable search would need to exploit the mechanism's structure: below the
insertion depth the deck behaves as a move-to-front list, above it as a queue that only
shifts upward, so positions are cumulative counts of outputs on one side of a card rather
than free integers. That reformulation is the next real piece of work, and it is only worth
doing if the mechanism is exactly right, which nothing here proves.

## 5. What remains open

- The mechanism. Non-rotating single-card-move decks are the one shape consistent with
  every measurement (4.2), but the slot layout and depth are undetermined and the family
  is a guess that fits, not a derivation. Multi-component machines were tried only
  because of the tail at 9/13/17, which section 2.5 shows to be mostly a double-counting
  artefact.
- The plaintext language and alphabet size. Nothing here distinguishes English from
  Finnish; both were run throughout.
- Whether the base-5 digits matter at all: 2.7 says no.

## 6. Suggested next steps

1. Read the community progress document before doing anything else; it was not reachable
   from the environment that produced this analysis.
2. The arithmetic-progression layout search is done (4.1) and did not discriminate. The
   decisive test for the surviving family is a constraint-based key search (4.2): find an
   initial deck, depth and slot set such that decrypting all nine messages visits only
   slot positions. Naive backtracking is hopeless (the first ~120 symbols branch before
   repeats constrain); a CP-SAT encoding over card positions per time step is the
   plausible route, and it only succeeds if the mechanism is exactly right. This is a constraint problem, not an n-gram hill-climb: decrypting
   under a candidate initial deck must visit only slot positions.
3. Use E4/E5 more precisely: the pattern of exactly which positions re-match after the
   divergence (runs of three, then a miss) is a direct measurement of how many cards one
   letter's move displaces, and any candidate must reproduce the run structure, not just the
   rate.
