#!/bin/sh
# Fetch the Project Gutenberg texts used as English/Finnish plaintext (GITenberg mirrors).
set -e
cd "$(dirname "$0")/.." && mkdir -p corpus && cd corpus
for r in GITenberg/Alice-s-Adventures-in-Wonderland_11 GITenberg/The-Adventures-of-Sherlock-Holmes_1661 GITenberg/Kalevala_7000; do
  [ -d "$(basename $r)" ] || git clone -q --depth 1 https://github.com/$r
done
