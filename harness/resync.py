import random, sys, collections
from fp import load_corpus
from mech import LookupDeck, CutDeck, Chao, RandGAK, text_to_idx, N
from mech2 import SpacedLookup, ChaoCtOnly
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
def profile(mk, nchange, trials=300, seed=5):
    """encrypt segment twice: original and with `nchange` letters at pos 21..21+nchange-1 replaced. return match fraction in
       windows: the changed region, next 20, next 20 after that."""
    rng=random.Random(seed); agg=[0,0,0]; cnt=[0,0,0]
    for _ in range(trials):
        st=rng.randrange(0,len(idx)-80); seg=idx[st:st+80]; seg2=list(seg)
        for j in range(21,21+nchange):
            seg2[j]=rng.choice([x for x in range(A) if x!=seg[j]])
        m1=mk(random.Random(rng.random())); ks=m1.__dict__.copy()
        import copy
        m2=copy.deepcopy(m1)
        c1=[m1.enc(p) for p in seg]; c2=[m2.enc(p) for p in seg2]
        for w,(a,b) in enumerate([(21,21+nchange),(21+nchange,41+nchange),(41+nchange,61+nchange)]):
            agg[w]+=sum(c1[t]==c2[t] for t in range(a,b)); cnt[w]+=b-a
    return [round(a/c,2) for a,c in zip(agg,cnt)]
cands={}
for op in ['cut_then_depth','move_depth','move_rel','swap_rel']:
    for k in [4,8,11,14,17,20,23,26,32,40]:
        for sp in [1,2,3,4]:
            cands[f"{op} k={k} sp={sp}"]=lambda r,op=op,k=k,sp=sp:SpacedLookup(A,r,op,k,sp)
        cands[f"{op} k={k} random"]=lambda r,op=op,k=k:LookupDeck(A,r,op,k,'random')
for k in [4,15,19,23]: cands[f"CutDeck k={k}"]=lambda r,k=k:CutDeck(A,r,k,'random')
for nad in [4,20,41]:
    cands[f"Chao nadir={nad}"]=lambda r,nad=nad:Chao(A,r,nad,1,2,1,freqs)
    cands[f"ChaoCtOnly nadir={nad} ext=1"]=lambda r,nad=nad:ChaoCtOnly(A,r,nad,1,freqs)
cands["RandGAK"]=lambda r:RandGAK(A,r)
print(f"lang={lang} space={use_space}  TARGET E4/E5: changed 0/4, next20 ~0.55, next20 ~0.05 | E1/W1: 4 diff, 4 same, 4 diff, 13 same")
rows=[]
for name,mk in cands.items():
    p4=profile(mk,4); p1=profile(mk,1); rows.append((p4[1],name,p4,p1))
rows.sort(reverse=True)
for s,name,p4,p1 in rows: print(f"{name:28s} 4-letter change: {p4}   1-letter change: {p1}")
