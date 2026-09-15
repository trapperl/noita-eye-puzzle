import random, math, sys, collections
from fp import load_corpus, dist_table
from mech import LookupDeck, text_to_idx, N
from mech2 import SpacedLookup, evaluate, T_ratio, T_sd, DMAX
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
res=[]
for op in ['cut_then_depth','move_depth']:
    for k in range(4,42):
        for sp,off in [(3,0),(3,1),(3,2),(2,0),(4,0),(1,0)]:
            mk=lambda r,op=op,k=k,sp=sp,off=off:SpacedLookup(A,r,op,k,sp,off)
            chi,acc=evaluate(mk,idx,nkeys=4,nsym=20000)
            # key variance: per-key d4 ratio spread
            d4=[]
            for j in range(4):
                rng=random.Random(100+j); m=mk(rng); st=rng.randrange(0,len(idx)-20000)
                seq=[m.enc(p) for p in idx[st:st+20000]]; d4.append(dist_table([seq],4)[3][3])
            res.append((chi,f"{op} k={k} sp={sp} off={off}",acc,d4))
res.sort()
print(f"lang={lang} space={use_space} A={A}")
print("TARGET       ",[round(x,2) for x in T_ratio[:20]])
for chi,name,acc,d4 in res[:20]:
    print(f"{chi:6.1f} {name:32s} {[round(x,2) for x in acc[:20]]} d4/key={[round(x,2) for x in d4]}")
