import random, math, sys, collections
from fp import load_corpus, dist_table, load_eyes
from mech import LookupDeck, CutDeck, Chao, PosKey, RandGAK, StreamFB, text_to_idx, N
DMAX=20
eyes=list(load_eyes().values()); TT=dist_table(eyes,DMAX)
T_ratio=[r[3] for r in TT]; T_sd=[math.sqrt(r[2]/N)/(r[2]/N) for r in TT]   # poisson sd of ratio
class SpacedLookup(LookupDeck):
    def __init__(s,A,rng,op,k,spacing,offset=0):
        super().__init__(A,rng,op,k,'top'); s.key=[(offset+i*spacing)%N for i in range(A)]
class ChaoCtOnly:
    """homophonic pt disk fixed; ct disk: cut at output, extract at ext, insert at nadir."""
    def __init__(s,A,rng,nadir,ext,freqs):
        s.ct=list(range(N)); rng.shuffle(s.ct)
        tot=sum(freqs); cells=[max(1,round(f/tot*N)) for f in freqs]
        while sum(cells)>N: cells[cells.index(max(cells))]-=1
        while sum(cells)<N: cells[cells.index(min(cells))]+=1
        s.pt=[a for a,c in enumerate(cells) for _ in range(c)]; rng.shuffle(s.pt); s.nadir=nadir; s.ext=ext
    def enc(s,p):
        i=s.pt.index(p); c=s.ct[i]; ct=s.ct[i:]+s.ct[:i]; x=ct.pop(s.ext); ct.insert(s.nadir,x); s.ct=ct; return c
def evaluate(mk, idx, nkeys=3, nsym=20000, seed=1):
    acc=[0.0]*DMAX
    for j in range(nkeys):
        rng=random.Random(seed+j); m=mk(rng); start=rng.randrange(0,len(idx)-nsym)
        seq=[m.enc(p) for p in idx[start:start+nsym]]
        for i,r in enumerate(dist_table([seq],DMAX)): acc[i]+=r[3]/nkeys
    sd_m=math.sqrt(nsym/N)/(nsym/N)/math.sqrt(nkeys)
    chi=sum((acc[d]-T_ratio[d])**2/(T_sd[d]**2+sd_m**2) for d in range(DMAX))
    return chi,acc
if __name__=='__main__':
    lang=sys.argv[1]; use_space=sys.argv[2]=='space'
    txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
    fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
    cands={}
    for op in ['cut_then_depth','move_depth','move_rel','swap_rel']:
        for k in range(0,42,2):
            for km in ['top','random']:
                cands[f"{op} k={k} key={km}"]=lambda r,op=op,k=k,km=km:LookupDeck(A,r,op,k,km)
            for sp in [2,3,4]:
                cands[f"{op} k={k} key=spaced{sp}"]=lambda r,op=op,k=k,sp=sp:SpacedLookup(A,r,op,k,sp)
    for k in range(1,42,2):
        for km in ['top','random']: cands[f"CutDeck k={k} key={km}"]=lambda r,k=k,km=km:CutDeck(A,r,k,km)
    for nad in [2,3,4,5,6,8,10,15,20,30,41,60,82]:
        for ec,ep,sh in [(1,2,1),(1,1,0),(2,2,1),(1,3,1),(3,3,1),(2,3,1)]:
            cands[f"Chao nadir={nad} ext={ec},{ep} shift={sh}"]=lambda r,nad=nad,ec=ec,ep=ep,sh=sh:Chao(A,r,nad,ec,ep,sh,freqs)
        for ext in [1,2,3,4]:
            cands[f"ChaoCtOnly nadir={nad} ext={ext}"]=lambda r,nad=nad,ext=ext:ChaoCtOnly(A,r,nad,ext,freqs)
    cands["PosKey (control)"]=lambda r:PosKey(A,r); cands["RandGAK (control)"]=lambda r:RandGAK(A,r)
    res=[]
    for name,mk in cands.items():
        chi,acc=evaluate(mk,idx); res.append((chi,name,acc))
    res.sort()
    print(f"lang={lang} space={use_space} A={A} ncand={len(cands)}")
    print("TARGET      ", [round(x,2) for x in T_ratio[:12]])
    for chi,name,acc in res[:30]: print(f"{chi:7.1f} {name:40s} {[round(x,2) for x in acc[:12]]}")
    print("control:",[ (round(c,1),n) for c,n,a in res if 'control' in n])
