"""Two-deck machines: plaintext deck P (letters, keyed order) and ciphertext deck C (83 symbols).
enc(p): i = index of p in P; c = C[i]; then P and C are each modified by a simple rule.
Scores both fingerprints and key-stability. Usage: python3 mech4.py en nospace"""
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
class TwoDeck:
    def __init__(s,rng,pmove,cmove,k,pdepth=None,homo=None):
        s.C=list(range(N)); rng.shuffle(s.C)
        if homo is None: s.P=list(range(A)); rng.shuffle(s.P)
        else:  # homophonic P deck of 83 cells
            tot=sum(homo); cells=[max(1,round(f/tot*N)) for f in homo]
            while sum(cells)>N: cells[cells.index(max(cells))]-=1
            while sum(cells)<N: cells[cells.index(min(cells))]+=1
            s.P=[a for a,c in enumerate(cells) for _ in range(c)]; rng.shuffle(s.P)
        s.pmove=pmove; s.cmove=cmove; s.k=k; s.pdepth=pdepth
    def enc(s,p):
        P,C=s.P,s.C; i=P.index(p); c=C[i]
        if s.pmove=='back': P.pop(i); P.append(p)
        elif s.pmove=='front': P.pop(i); P.insert(0,p)
        elif s.pmove=='depth': P.pop(i); P.insert(s.pdepth,p)
        elif s.pmove=='swapnext': j=(i+1)%len(P); P[i],P[j]=P[j],P[i]
        elif s.pmove=='rotate': P[:]=P[1:]+P[:1]
        # 'none': P static
        if s.cmove=='depth': C.pop(i); C.insert(s.k,c)
        elif s.cmove=='back': C.pop(i); C.append(c)
        elif s.cmove=='front': C.pop(i); C.insert(0,c)
        elif s.cmove=='rel': C.pop(i); C.insert((i+s.k)%N,c)
        elif s.cmove=='swap': j=(i+s.k)%N; C[i],C[j]=C[j],C[i]
        elif s.cmove=='rotate': C[:]=C[s.k:]+C[:s.k]
        return c
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
fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
cands={}
for pm in ['back','front','swapnext','rotate','none']:
    for cm in ['depth','rel','swap']:
        for k in list(range(0,30))+[35,41,50,60,70,82]:
            cands[f"P:{pm} C:{cm} k={k}"]=lambda g,pm=pm,cm=cm,k=k:TwoDeck(g,pm,cm,k)
    for cm in ['back','front']:
        cands[f"P:{pm} C:{cm}"]=lambda g,pm=pm,cm=cm:TwoDeck(g,pm,cm,0)
for pd in [2,3,4,5,8,13]:
    for cm in ['depth','rel']:
        for k in [1,2,3,4,5,6,8,10,13,20,30,41]:
            cands[f"P:depth{pd} C:{cm} k={k}"]=lambda g,pd=pd,cm=cm,k=k:TwoDeck(g,'depth',cm,k,pd)
for pm in ['back','front','swapnext']:
    for k in [1,2,3,4,5,8,13,20,41,82]:
        cands[f"Phomo:{pm} C:depth k={k}"]=lambda g,pm=pm,k=k:TwoDeck(g,pm,'depth',k,None,freqs)
print(f"lang={lang} space={use_space} A={A} ncand={len(cands)}; target d1-6=[0,0.41,0.74,2.16,0.92,1.01]; resync4=0.55",flush=True)
rows=[]
for name,mk in cands.items():
    acc,spr=curve(mk); d=dev8(acc); rs=resync(mk)
    rows.append((d+40*(rs-0.55)**2+(10 if spr>1 else 0),d,rs,spr,name,acc))
rows.sort()
print(f"{'joint':>6} {'dev8':>5} {'rs4':>4} {'d4spr':>5}  mechanism                  d1..d8")
for j,d,rs,spr,name,acc in rows[:40]: print(f"{j:6.1f} {d:5.1f} {rs:4.2f} {spr:5.2f}  {name:26s} {[round(x,2) for x in acc]}")
