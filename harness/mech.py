import random, math, sys, itertools
from fp import load_corpus, dist_table, load_eyes
N=83
TARGET=[0.00,0.41,0.74,2.16,0.92,1.01,1.02,0.95,1.56,0.97,0.89,0.63]

def text_to_idx(txt, alpha, use_space):
    m={c:i for i,c in enumerate(alpha)}
    if use_space: m[' ']=len(alpha)
    return [m[c] for c in txt if c in m], len(m)

# ---------- mechanism family ----------
class LookupDeck:
    """output = deck[key[p]]; then post-op on that card."""
    def __init__(s, A, rng, op, k, keymode):
        s.deck=list(range(N)); rng.shuffle(s.deck)
        if keymode=='top': s.key=list(range(A))
        elif keymode=='random': s.key=rng.sample(range(N),A)
        elif keymode=='spaced': s.key=[(i*(N//A))%N for i in range(A)]
        s.op=op; s.k=k
    def enc(s,p):
        i=s.key[p]; d=s.deck; c=d[i]
        if s.op=='move_depth':      # remove card, insert at depth k
            d.pop(i); d.insert(s.k,c)
        elif s.op=='move_rel':      # remove card, insert k below its own position
            d.pop(i); d.insert((i+s.k)%N,c)
        elif s.op=='swap_abs':      # swap with position k
            d[i],d[s.k]=d[s.k],d[i]
        elif s.op=='swap_rel':
            j=(i+s.k)%N; d[i],d[j]=d[j],d[i]
        elif s.op=='cut_then_depth':  # cut so card below output is top, then insert output at depth k
            d.pop(i); d[:]=d[i:]+d[:i]; d.insert(s.k,c)
        elif s.op=='rotate':        # rotate whole deck by k after output
            d[:]=d[s.k:]+d[:s.k]
        elif s.op=='rot_then_depth':
            d.pop(i); d[:]=d[s.k:]+d[:s.k]; d.insert(0,c) if False else d.insert(s.k,c)
        return c
class CutDeck:
    """cut deck by key[p] (rotate), output top, then move top to depth k."""
    def __init__(s,A,rng,k,keymode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.k=k
        s.key=list(range(1,A+1)) if keymode=='top' else rng.sample(range(1,N),A)
    def enc(s,p):
        d=s.deck; r=s.key[p]; d[:]=d[r:]+d[:r]; c=d.pop(0); d.insert(s.k,c); return c
class Chao:
    """Chaocipher generalised to 83 cells. pt disk: 83 cells of letters (homophonic); ct disk: 83 symbols.
       enc: i=index of p in pt (first from zenith); c=ct[i]; permute ct: rotate to bring c to zenith, extract ct[1], insert at nadir;
       permute pt: rotate to bring p-cell to zenith, rotate one more, extract pt[2], insert at nadir."""
    def __init__(s,A,rng,nadir,ext_ct=1,ext_pt=2,pt_shift=1,freqs=None):
        s.ct=list(range(N)); rng.shuffle(s.ct)
        # homophonic pt disk: allocate cells proportional to freq
        if freqs is None: freqs=[1]*A
        tot=sum(freqs); cells=[max(1,round(f/tot*N)) for f in freqs]
        while sum(cells)>N: cells[cells.index(max(cells))]-=1
        while sum(cells)<N: cells[cells.index(min(cells))]+=1
        s.pt=[a for a,c in enumerate(cells) for _ in range(c)]; rng.shuffle(s.pt)
        s.nadir=nadir; s.ext_ct=ext_ct; s.ext_pt=ext_pt; s.pt_shift=pt_shift
    def enc(s,p):
        i=s.pt.index(p); c=s.ct[i]
        ct=s.ct[i:]+s.ct[:i]; x=ct.pop(s.ext_ct); ct.insert(s.nadir,x); s.ct=ct
        pt=s.pt[i:]+s.pt[:i]; pt=pt[s.pt_shift:]+pt[:s.pt_shift]; x=pt.pop(s.ext_pt); pt.insert(s.nadir,x); s.pt=pt
        return c
class PosKey:
    def __init__(s,A,rng): s.rng=rng; s.perms=[]; s.A=A
    def enc(s,p):
        perm=s.rng.sample(range(N),s.A); return perm[p]
class RandGAK:
    def __init__(s,A,rng):
        s.deck=list(range(N)); rng.shuffle(s.deck)
        s.perms=[rng.sample(range(N),N) for _ in range(A)]
    def enc(s,p):
        pm=s.perms[p]; s.deck=[s.deck[pm[i]] for i in range(N)]; return s.deck[0]
class StreamFB:
    def __init__(s,A,rng,a,c0): s.S=rng.randrange(N); s.a=a; s.c0=c0
    def enc(s,p):
        c=(p+s.S)%N; s.S=(s.a*s.S+s.c0+c)%N; return c

def run(mk, idx, nsym, rng):
    m=mk(rng); return [m.enc(p) for p in idx[:nsym]]
def score(fpv): return sum((a-b)**2 for a,b in zip(fpv,TARGET[:len(fpv)]))
def fpr(seq,dmax=12): return [round(r[3],2) for r in dist_table([seq],dmax)]

if __name__=='__main__':
    lang=sys.argv[1] if len(sys.argv)>1 else 'en'
    use_space=(sys.argv[2]=='space') if len(sys.argv)>2 else False
    txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
    import collections
    fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
    NS=30000; rng=random.Random(7); results=[]
    cands={}
    for op in ['move_depth','move_rel','swap_abs','swap_rel','cut_then_depth','rotate']:
        for k in [0,1,2,3,4,5,6,8,10,20,41,82]:
            for km in ['top','random','spaced']:
                cands[f"Lookup op={op} k={k} key={km}"]=lambda r,op=op,k=k,km=km:LookupDeck(A,r,op,k,km)
    for k in [1,2,3,4,5,6,8,10,20,41,82]:
        for km in ['top','random']:
            cands[f"CutDeck k={k} key={km}"]=lambda r,k=k,km=km:CutDeck(A,r,k,km)
    for nad in [2,3,4,5,10,20,41,60,82]:
        for ec,ep,sh in [(1,2,1),(1,1,0),(2,2,1),(1,3,1),(3,3,1)]:
            cands[f"Chao nadir={nad} ext={ec},{ep} shift={sh} hom"]=lambda r,nad=nad,ec=ec,ep=ep,sh=sh:Chao(A,r,nad,ec,ep,sh,freqs)
            cands[f"Chao nadir={nad} ext={ec},{ep} shift={sh} flat"]=lambda r,nad=nad,ec=ec,ep=ep,sh=sh:Chao(A,r,nad,ec,ep,sh,None)
    cands["PosKey (control)"]=lambda r:PosKey(A,r)
    cands["RandGAK (control)"]=lambda r:RandGAK(A,r)
    for a in [1,2,5,17]:
        cands[f"StreamFB a={a}"]=lambda r,a=a:StreamFB(A,r,a,1)
    for name,mk in cands.items():
        seq=run(mk,idx,NS,rng); f=fpr(seq); results.append((score(f),name,f))
    results.sort()
    print(f"lang={lang} space={use_space} A={A}  TARGET {TARGET}")
    for s,name,f in results[:25]: print(f"{s:6.2f} {name:45s} {f}")
    print("...")
    for s,name,f in results[-5:]: print(f"{s:6.2f} {name:45s} {f}")
