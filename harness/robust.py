import random, sys, collections, math, copy
from fp import load_corpus, dist_table, load_eyes
from mech import LookupDeck, text_to_idx, N
from mech2 import SpacedLookup
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
TT=dist_table(list(load_eyes().values()),8); obs=[r[1] for r in TT]; exp=[r[2]/83 for r in TT]
def dev8(r):
    s=0
    for d in range(8):
        mu=max(exp[d]*r[d],1e-3); ll=obs[d]*math.log(mu)-mu; lls=(obs[d]*math.log(obs[d])-obs[d]) if obs[d]>0 else 0
        s+=2*(lls-ll)
    return s
def resync(mk,nchange,trials=200,seed=3):
    rng=random.Random(seed); e=n=0
    for _ in range(trials):
        st=rng.randrange(0,len(idx)-60); seg=idx[st:st+60]; seg2=list(seg)
        for j in range(21,21+nchange): seg2[j]=rng.choice([x for x in range(A) if x!=seg[j]])
        m1=mk(random.Random(rng.random())); m2=copy.deepcopy(m1)
        c1=[m1.enc(p) for p in seg]; c2=[m2.enc(p) for p in seg2]
        e+=sum(c1[t]==c2[t] for t in range(21+nchange,41+nchange)); n+=20
    return e/n
print(f"lang={lang} space={use_space} A={A}   target d1-6=[0,0.41,0.74,2.16,0.92,1.01] resync4=0.55")
print(f"{'mech':26s} {'dev8':>5} {'d4 mean':>7} {'d4 per key':30s} {'d1-6 mean':40s} rs4  rs1")
for keymode in ['random','top','spaced3']:
    for k in [11,15,19,21,23,25,27,31,35,41]:
        if keymode=='spaced3': mk=lambda r,k=k:SpacedLookup(A,r,'move_depth',k,3)
        else: mk=lambda r,k=k,km=keymode:LookupDeck(A,r,'move_depth',k,km)
        accs=[]
        for j in range(6):
            rng=random.Random(50+j); m=mk(rng); st=rng.randrange(0,len(idx)-20000)
            seq=[m.enc(p) for p in idx[st:st+20000]]; accs.append([r[3] for r in dist_table([seq],8)])
        mean=[sum(a[d] for a in accs)/6 for d in range(8)]
        print(f"move_depth k={k:2d} {keymode:8s} {dev8(mean):5.1f} {mean[3]:7.2f} {str([round(a[3],2) for a in accs]):30s} {str([round(x,2) for x in mean[:6]]):40s} {resync(mk,4):.2f} {resync(mk,1):.2f}",flush=True)
