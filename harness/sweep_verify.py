"""Re-score the best stable configs from the C sweep on statistics they were not selected on:
re-match rate after a 4-letter change, IoC ratio, and full distance-curve deviance out to d=24 (deduplicated target).
Usage: python3 sweep_verify.py fi space 300"""
import sys, math, random, copy, collections
from fp import load_corpus, dist_table, load_eyes, ioc
from mech import text_to_idx, N
lang=sys.argv[1]; use_space=sys.argv[2]=='space'; TOP=int(sys.argv[3])
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
fr=collections.Counter(idx); order=[a for a,_ in fr.most_common()]+[a for a in range(A) if a not in fr]; rank_freq={a:i for i,a in enumerate(order)}
# deduplicated target
m=load_eyes(); names=list(m); DM=24
obs=[];exp=[]
for d in range(1,DM+1):
    e=c=0
    for j,nj in enumerate(names):
        v=m[nj]
        for t in range(len(v)-d):
            if any(len(m[ni])>t+d and m[ni][t:t+d+1]==v[t:t+d+1] for ni in names[:j]): continue
            c+=1; e+=v[t]==v[t+d]
    obs.append(e); exp.append(c/N)
def dev(r,lo,hi):
    s=0
    for d in range(lo,hi):
        mu=max(exp[d]*r[d],1e-3); ll=obs[d]*math.log(mu)-mu; lls=(obs[d]*math.log(obs[d])-obs[d]) if obs[d]>0 else 0
        s+=2*(lls-ll)
    return s
class M:
    def __init__(s,rng,k,a,sp,mode):
        s.deck=list(range(N)); rng.shuffle(s.deck); s.k=k
        s.slot=[(a+sp*(rank_freq[j] if mode else j))%N for j in range(A)]
    def enc(s,p):
        d=s.deck; i=s.slot[p]; c=d.pop(i); d.insert(s.k,c); return c
def curve(mk,nkeys=4,nsym=20000,seed=101):
    acc=[0.0]*DM; io=0
    for j in range(nkeys):
        rng=random.Random(seed+j); mm=mk(rng); st=rng.randrange(0,len(idx)-nsym)
        seq=[mm.enc(p) for p in idx[st:st+nsym]]; r=[x[3] for x in dist_table([seq],DM)]; io+=ioc([seq])/nkeys
        for d in range(DM): acc[d]+=r[d]/nkeys
    return acc,io
def resync(mk,nchange=4,trials=150,seed=3):
    rng=random.Random(seed); e=n=0
    for _ in range(trials):
        st=rng.randrange(0,len(idx)-60); seg=idx[st:st+60]; seg2=list(seg)
        for j in range(21,21+nchange): seg2[j]=rng.choice([x for x in range(A) if x!=seg[j]])
        m1=mk(random.Random(rng.random())); m2=copy.deepcopy(m1)
        c1=[m1.enc(p) for p in seg]; c2=[m2.enc(p) for p in seg2]
        e+=sum(c1[t]==c2[t] for t in range(21+nchange,41+nchange)); n+=20
    return e/n
rows=[]
for line in open(f'../results/sweep_{lang}.txt'):
    p=line.split()
    if len(p)<14: continue
    k,a,s,mode=map(int,p[:4]); d8=float(p[4]); spr=float(p[5])
    if spr<0.6: rows.append((d8,k,a,s,mode))
rows.sort(); rows=rows[:TOP]
print(f"lang={lang} space={use_space}: re-scoring {len(rows)} configs. Target: resync4 0.55, IoC 1.066, tail d9-24 dev ~16 (floor), d1-8 dev ~8 (floor)")
out=[]
for d8,k,a,s,mode in rows:
    mk=lambda g,k=k,a=a,s=s,mode=mode:M(g,k,a,s,mode)
    acc,io=curve(mk); rs=resync(mk)
    out.append((dev(acc,0,8)+dev(acc,8,24)+40*(rs-0.55)**2, dev(acc,0,8), dev(acc,8,24), rs, io, k,a,s,mode, acc))
out.sort()
print(f"{'joint':>6} {'d1-8':>5} {'d9-24':>5} {'rs4':>4} {'IoC':>5}   k   a   s md  r1..r6 | r9,13,17")
for j,d1,d2,rs,io,k,a,s,mode,acc in out[:25]:
    print(f"{j:6.1f} {d1:5.1f} {d2:5.1f} {rs:4.2f} {io:5.3f} {k:3d} {a:3d} {s:3d} {mode:2d}  {[round(x,2) for x in acc[:6]]} | {[round(acc[i],2) for i in (8,12,16)]}")
print("resync distribution over all re-scored:",sorted(collections.Counter(round(x[3],1) for x in out).items()))
