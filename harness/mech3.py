import random, sys, collections, math, copy
from fp import load_corpus, dist_table, load_eyes
from mech import text_to_idx, N
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
DM=24
TT=dist_table(list(load_eyes().values()),DM); obs=[r[1] for r in TT]; exp=[r[2]/83 for r in TT]
def dev(r,upto=DM):
    s=0
    for d in range(upto):
        mu=max(exp[d]*r[d],1e-3); ll=obs[d]*math.log(mu)-mu; lls=(obs[d]*math.log(obs[d])-obs[d]) if obs[d]>0 else 0
        s+=2*(lls-ll)
    return s
def slots(mode,rng):
    if mode=='top': return list(range(A))
    if mode=='spaced3': return [(3*i)%N for i in range(A)]
    if mode=='random': return rng.sample(range(N),A)
class RotMove:
    """c=deck[slot[p]]; pop; insert at depth k (abs) or slot+k (rel); then rotate deck by constant r."""
    def __init__(s,rng,k,r,mode,rel=False):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.slot=slots(mode,rng); s.k=k; s.r=r; s.rel=rel
    def enc(s,p):
        d=s.deck; i=s.slot[p]; c=d.pop(i); d.insert((i+s.k)%N if s.rel else s.k,c); d[:]=d[s.r:]+d[:s.r]; return c
class TwoMove:
    """c=deck[slot[p]]; move c to depth k1; then move card at position k2 to top (or to depth k3)."""
    def __init__(s,rng,k1,k2,mode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.slot=slots(mode,rng); s.k1=k1; s.k2=k2
    def enc(s,p):
        d=s.deck; c=d.pop(s.slot[p]); d.insert(s.k1,c); x=d.pop(s.k2); d.insert(0,x); return c
class LetterDepth:
    """c=deck[slot[p]]; move c to depth dep[p] (letter-dependent), optional constant rotation r."""
    def __init__(s,rng,r,mode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.slot=slots(mode,rng); s.dep=[rng.randrange(1,N) for _ in range(A)]; s.r=r
    def enc(s,p):
        d=s.deck; c=d.pop(s.slot[p]); d.insert(s.dep[p],c); d[:]=d[s.r:]+d[:s.r]; return c
class ChaoU:
    """Chaocipher with 83-cell homophonic pt disk and separate nadirs/extract offsets for ct and pt disks."""
    def __init__(s,rng,nct,npt,ect,ept):
        s.ct=list(range(N)); rng.shuffle(s.ct)
        tot=sum(freqs); cells=[max(1,round(f/tot*N)) for f in freqs]
        while sum(cells)>N: cells[cells.index(max(cells))]-=1
        while sum(cells)<N: cells[cells.index(min(cells))]+=1
        s.pt=[a for a,c in enumerate(cells) for _ in range(c)]; rng.shuffle(s.pt); s.nct=nct; s.npt=npt; s.ect=ect; s.ept=ept
    def enc(s,p):
        i=s.pt.index(p); c=s.ct[i]
        ct=s.ct[i:]+s.ct[:i]; x=ct.pop(s.ect); ct.insert(s.nct,x); s.ct=ct
        pt=s.pt[i:]+s.pt[:i]; pt=pt[1:]+pt[:1]; x=pt.pop(s.ept); pt.insert(s.npt,x); s.pt=pt
        return c
class MoveNadir:
    """deck; c=deck[slot[p]]; c moved to a nadir pointer that advances by step each time (moving insertion point)."""
    def __init__(s,rng,step,mode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.slot=slots(mode,rng); s.nad=41; s.step=step
    def enc(s,p):
        d=s.deck; c=d.pop(s.slot[p]); d.insert(s.nad,c); s.nad=(s.nad+s.step)%N; return c
def curve(mk,nkeys=4,nsym=15000,seed=11):
    acc=[0.0]*DM; per=[]
    for j in range(nkeys):
        rng=random.Random(seed+j); m=mk(rng); st=rng.randrange(0,len(idx)-nsym)
        seq=[m.enc(p) for p in idx[st:st+nsym]]; r=[x[3] for x in dist_table([seq],DM)]; per.append(r[3])
        for d in range(DM): acc[d]+=r[d]/nkeys
    return acc,per
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
for mode in ['top','spaced3','random']:
    for k in [4,8,12,16,20,24,28,32,40]:
        for r in [1,2,3,4,5,7,9,13,20,41,82]:
            cands[f"RotMove k={k} r={r} {mode}"]=lambda g,k=k,r=r,mode=mode:RotMove(g,k,r,mode)
            cands[f"RotMoveRel k={k} r={r} {mode}"]=lambda g,k=k,r=r,mode=mode:RotMove(g,k,r,mode,True)
    for k1 in [4,9,13,20,30,41]:
        for k2 in [4,9,13,20,30,41,82]:
            cands[f"TwoMove k1={k1} k2={k2} {mode}"]=lambda g,k1=k1,k2=k2,mode=mode:TwoMove(g,k1,k2,mode)
    for r in [0,1,2,3,4,9]:
        cands[f"LetterDepth r={r} {mode}"]=lambda g,r=r,mode=mode:LetterDepth(g,r,mode)
    for st in [1,2,3,4,5,9,13]:
        cands[f"MoveNadir step={st} {mode}"]=lambda g,st=st,mode=mode:MoveNadir(g,st,mode)
for nct in [3,4,5,9,13,41]:
    for npt in [3,4,5,9,13,41]:
        for ect,ept in [(1,2),(1,1),(2,2)]:
            cands[f"ChaoU nct={nct} npt={npt} e={ect},{ept}"]=lambda g,a=nct,b=npt,c=ect,d=ept:ChaoU(g,a,b,c,d)
print(f"lang={lang} space={use_space} A={A} ncand={len(cands)}; target d1-6=[0,0.41,0.74,2.16,0.92,1.01], tail 9,13,17 high / 15,19,22 low; resync4=0.55",flush=True)
rows=[]
for name,mk in cands.items():
    acc,per=curve(mk); d24=dev(acc); d8=dev(acc,8); rs=resync(mk)
    spread=max(per)-min(per)
    joint=d24+40*(rs-0.55)**2+ (10 if spread>1.0 else 0)
    rows.append((joint,d24,d8,rs,spread,name,acc))
rows.sort()
print(f"{'joint':>6} {'dev24':>6} {'dev8':>5} {'rs4':>4} {'d4spr':>5}  mechanism                       d1-6 | d9,13,17 | d15,19,22")
for j,d24,d8,rs,sp,name,acc in rows[:40]:
    print(f"{j:6.1f} {d24:6.1f} {d8:5.1f} {rs:4.2f} {sp:5.2f}  {name:30s} {[round(x,2) for x in acc[:6]]} | {[round(acc[i],2) for i in (8,12,16)]} | {[round(acc[i],2) for i in (14,18,21)]}")
