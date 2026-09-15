# Data sources

`noita_eye_data_trigrams.csv` is the community transcription of the nine eye messages as
trigram values 0..82 under the orthodox reading order. It is copied verbatim from
ngraham20/NoitaCryptographyResearch (`eye/reference/noita_eye_data_trigrams.csv`), which in
turn derives from the community "Noita Eye Data" spreadsheet. Credit for the transcription
belongs to the Noita eye-message community; it is included here only so the harness runs
without external fetches. The values are facts about the game's glyphs.

Row layout: column 1 is a row index, column 2 the message name, columns 3.. the trigram
values in reading order. Message lengths: East 1 = 99, West 1 = 103, East 2 = 118,
West 2 = 102, East 3 = 137, West 3 = 124, East 4 = 119, West 4 = 120, East 5 = 114.
