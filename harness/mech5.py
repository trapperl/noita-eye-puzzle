"""Conditional-alphabet ciphers: the class of the previous ciphertext symbol (or previous plaintext letter)
selects which of m substitution alphabets enciphers the current letter. Exact re-sync and (optionally) no doubles
by construction. Usage: python3 mech5.py en nospace"""
import random, sys, collections, math, copy
from fp import load_corpus, dist_table, load_eyes
from mech import text_to_idx, N
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
TT=dist_table(list(load_eyes().values()),8); obs=[r[1] for r in TT]; exp=[r[2]/83 for r in TT]
def dev8(r):
    s=0
    for d in range(8):
        mu=max(exp[d]*r[d],1e-3); ll=obs[d]*math.log(mu)-mu; lls=(obs[d]*math.log(obs[d])-obs[d]) if obs[d]>0 else 0
        s+=2*(lls-ll)
    return s
class CondAlpha:
    """m classes; cls[c] = class of symbol c (balanced random partition). alphabets[r] maps letter -> symbol.
       mode 'any': alphabet r draws from all symbols; 'excl': never from class r (no doubles by design);
       'next': alphabet r draws only from class (r+1)%m (a ring). cond='ct' uses class of previous ciphertext,
       'pt' uses class of previous plaintext letter (letters partitioned into m classes)."""
    def __init__(s,rng,m,mode,cond,homo=False):
        s.m=m; s.cond=cond
        syms=list(range(N)); rng.shuffle(syms); s.cls=[0]*N
        for i,c in enumerate(syms): s.cls[c]=i%m
        s.pcls=[i%m for i in range(A)]; rng.shuffle(s.pcls)
        s.alph=[]
        for r in range(m):
            if mode=='any': pool=list(range(N))
            elif mode=='excl': pool=[c for c in range(N) if s.cls[c]!=r]
            else: pool=[c for c in range(N) if s.cls[c]==(r+1)%m]
            rng.shuffle(pool)
            if len(pool)<A: pool=(pool*((A//len(pool))+1))  # allow reuse if class too small
            s.alph.append(pool[:A])
        s.prev=rng.randrange(m); s.prevp=rng.randrange(A)
    def enc(s,p):
        r=s.prev if s.cond=='ct' else s.pcls[s.prevp]
        c=s.alph[r][p]; s.prev=s.cls[c]; s.prevp=p; return c
def curve(mk,nkeys=4,nsym=15000,seed=11):
    acc=[0.0]*8; d4=[]
    for j in range(nkeys):
        rng=random.Random(seed+j); m=mk(rng); st=rng.randrange(0,len(idx)-nsym)
        seq=[m.enc(p) for p in idx[st:st+nsym]]; r=[x[3] for x in dist_table([seq],8)]; d4.append(r[3])
        for d in range(8): acc[d]+=r[d]/nkeys
    return acc,max(d4)-min(d4)
def resync(mk,nchange=4,trials=150,seed=3):
    rng=random.Random(seed); e=n=0
    for _ in range(trials):
        st=rng.randrange(0,len(idx)-60); seg=idx[st:st+60]; seg2=list(seg)
        for j in range(21,21+nchange): seg2[j]=rng.choice([x for x in range(A) if x!=seg[j]])
        m1=mk(random.Random(rng.random())); m2=copy.deepcopy(m1)
        c1=[m1.enc(p) for p in seg]; c2=[m2.enc(p) for p in seg2]
        e+=sum(c1[t]==c2[t] for t in range(21+nchange,41+nchange)); n+=20
    return e/n
cands={}
for m in [2,3,4,5,6,8,10]:
    for mode in ['any','excl','next']:
        for cond in ['ct','pt']:
            cands[f"m={m} {mode} cond={cond}"]=lambda g,m=m,mode=mode,cond=cond:CondAlpha(g,m,mode,cond)
print(f"lang={lang} space={use_space} A={A}; target d1-6=[0,0.41,0.74,2.16,0.92,1.01]; resync4=0.55")
rows=[]
for name,mk in cands.items():
    acc,spr=curve(mk); d=dev8(acc); rs=resync(mk); rows.append((d+40*(rs-0.55)**2,d,rs,spr,name,acc))
rows.sort()
print(f"{'joint':>6} {'dev8':>5} {'rs4':>4} {'d4spr':>5}  mechanism            d1..d8")
for j,d,rs,spr,name,acc in rows: print(f"{j:6.1f} {d:5.1f} {rs:4.2f} {spr:5.2f}  {name:20s} {[round(x,2) for x in acc]}")
