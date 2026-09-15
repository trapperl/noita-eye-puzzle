"""Under the non-rotating move-to-depth deck, how many of the next 23 positions match after a 1-, 2- or 4-letter change?
Compares with E1/W1 (1 changed block at 26, 16 of the next 23 match) and E4/E5 (4-letter block at 22, 11 of next 20 match).
Usage: python3 perturb.py fi space 60"""
import sys, random, copy, collections
from fp import load_corpus
from mech import text_to_idx, N
lang=sys.argv[1]; use_space=sys.argv[2]=='space'; TOP=int(sys.argv[3])
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
fr=collections.Counter(idx); order=[a for a,_ in fr.most_common()]+[a for a in range(A) if a not in fr]; rank_freq={a:i for i,a in enumerate(order)}
class M:
    def __init__(s,rng,k,a,sp,mode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.k=k; s.slot=[(a+sp*(rank_freq[j] if mode else j))%N for j in range(A)]
    def enc(s,p):
        d=s.deck; i=s.slot[p]; c=d.pop(i); d.insert(s.k,c); return c
def dist(mk,nchange,window,trials=400,seed=9):
    rng=random.Random(seed); out=[]
    for _ in range(trials):
        st=rng.randrange(0,len(idx)-70); seg=idx[st:st+70]; seg2=list(seg)
        for j in range(25,25+nchange): seg2[j]=rng.choice([x for x in range(A) if x!=seg[j]])
        m1=mk(random.Random(rng.random())); m2=copy.deepcopy(m1)
        c1=[m1.enc(p) for p in seg]; c2=[m2.enc(p) for p in seg2]
        out.append(sum(c1[t]==c2[t] for t in range(25+nchange,25+nchange+window)))
    return out
rows=[]
for line in open(f'../results/sweep_{lang}.txt'):
    p=line.split()
    if len(p)<14: continue
    if float(p[5])<0.6: rows.append((float(p[4]),tuple(map(int,p[:4]))))
rows.sort(); cfgs=[c for _,c in rows[:TOP]]
print(f"lang={lang}: {len(cfgs)} configs. E1/W1: 16/23 after 1 block; E4/E5: 11/20 after 4-letter block")
agg={1:[],2:[],4:[]}
for k,a,s,mode in cfgs:
    mk=lambda g,k=k,a=a,s=s,mode=mode:M(g,k,a,s,mode)
    for n,w in [(1,23),(2,23),(4,20)]: agg[n]+=dist(mk,n,w,trials=60)
for n,w in [(1,23),(2,23),(4,20)]:
    d=agg[n]; mean=sum(d)/len(d); thr=16 if n<4 else 11
    print(f"  {n}-letter change, next {w}: mean matches {mean:5.2f} ({mean/w:.2f});  P(matches >= {thr}) = {sum(x>=thr for x in d)/len(d):.3f};  P(>= {w-2}) = {sum(x>=w-2 for x in d)/len(d):.3f}")
    h=collections.Counter(d); print("    histogram:",[h[i] for i in range(w+1)])
