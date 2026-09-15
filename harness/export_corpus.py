"""Write corpus/<lang>.idx (plaintext letter indices as bytes), corpus/<lang>.meta (alphabet size and
frequency order, every letter included) and corpus/target.txt (eye-data distance counts) for sweep.c."""
import collections
from fp import load_corpus, dist_table, load_eyes
from mech import text_to_idx
for lang,sp in [('en',False),('fi',True)]:
    txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,sp)
    fr=collections.Counter(idx); order=[a for a,_ in fr.most_common()]+[a for a in range(A) if a not in fr]
    open(f'../corpus/{lang}.idx','wb').write(bytes(idx))
    open(f'../corpus/{lang}.meta','w').write(f"{A}\n"+" ".join(map(str,order))+"\n")
TT=dist_table(list(load_eyes().values()),8)
open('../corpus/target.txt','w').write("\n".join(f"{r[1]} {r[2]/83:.4f}" for r in TT)+"\n")
print("wrote corpus/{en,fi}.idx, .meta, target.txt")
