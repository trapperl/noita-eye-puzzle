"""Structural tests on the eye-message trigram data (no simulation). Reproduces every number in FINDINGS.md
section 2. Run from the harness/ directory: python3 structure.py"""
import collections, itertools, math, random
from fp import load_eyes, dist_table, ioc
N=83
m=load_eyes(); names=list(m); seqs=list(m.values())
allv=[x for v in seqs for x in v]; cnt=collections.Counter(allv)
print("== basic"); print("symbols",len(allv),"distinct",len(cnt),"IoC x83",round(ioc(seqs),3),"most/least common",cnt.most_common(3),cnt.most_common()[-3:])
e=len(allv)/N; print("chi2 vs uniform",round(sum((cnt[k]-e)**2/e for k in range(N)),1),"(df 82)")

print("\n== shared prefixes (positions agreeing with the group's first member, 1-based)")
for g in (['East 1','West 1','East 2'],['East 4','West 4','East 5'],['West 2','East 3','West 3']):
    ref=m[g[0]]
    for o in g[1:]:
        v=m[o]; agree=[t+1 for t in range(min(len(v),len(ref))) if v[t]==ref[t]]
        print(f"  {g[0]} vs {o}: first symbols {ref[0]},{v[0]}; agree at {agree[:40]}{' ...' if len(agree)>40 else ''}")

print("\n== re-sync profiles after divergence (matches per 10-position bin)")
for x,y in [('East 4','East 5'),('West 4','East 5'),('East 4','West 4'),('East 1','West 1')]:
    a,b=m[x],m[y]; div=next(t for t in range(1,len(a)) if a[t]!=b[t])
    bins=[f"{s+1}-{min(s+10,len(a),len(b))}:{sum(a[t]==b[t] for t in range(s,min(s+10,len(a),len(b))))}" for s in range(div,min(len(a),len(b)),10)]
    print(f"  {x}/{y} diverge at {div+1}: {bins[:6]}")

print("\n== same-position coincidence, unrelated pairs, positions >= 27")
related={frozenset(p) for p in [('East 1','West 1'),('East 4','East 5'),('West 4','East 5'),('East 1','East 2'),('West 1','East 2'),('East 4','West 4')]}
e=n=0
for x,y in itertools.combinations(names,2):
    if frozenset((x,y)) in related: continue
    a,b=m[x],m[y]
    for t in range(26,min(len(a),len(b))): n+=1; e+=a[t]==b[t]
print(f"  {e}/{n} = {e/n:.4f}; chance {1/N:.4f} -> {n/N:.1f}; a reused letter keystream would give ~{0.065*n:.0f}")

print("\n== distance-d repeats, raw and with shared regions deduplicated")
raw=dist_table(seqs,24)
def dedup(dmax=24):
    out=[]
    for d in range(1,dmax+1):
        e=c=0
        for j,nj in enumerate(names):
            v=m[nj]
            for t in range(len(v)-d):
                if any(len(m[ni])>t+d and m[ni][t:t+d+1]==v[t:t+d+1] for ni in names[:j]): continue
                c+=1; e+=v[t]==v[t+d]
        exp=c/N; out.append((d,e,c,exp,(e-exp)/math.sqrt(exp*(1-1/N))))
    return out
print("   d  raw obs/exp  z     | dedup obs/exp  z")
for (d,e1,c1,r1,z1),(_,e2,c2,x2,z2) in zip(raw,dedup()):
    print(f"  {d:2d}  {e1:3d}/{c1/N:5.1f} {z1:+5.2f} | {e2:3d}/{x2:5.1f} {z2:+5.2f}")

print("\n== cyclic-homophone test: symbols b occurring exactly once in every interval between consecutive a's (>=4 intervals)")
iv=collections.defaultdict(list)
for v in seqs:
    pos=collections.defaultdict(list)
    for t,x in enumerate(v): pos[x].append(t)
    for a,ps in pos.items():
        for i in range(len(ps)-1): iv[a].append(v[ps[i]+1:ps[i+1]])
hits=[(a,[b for b in range(N) if b!=a and all(w.count(b)==1 for w in iv[a])]) for a in range(N) if len(iv[a])>=4]
print("  candidates:",[(a,b) for a,b in hits if b],"| symbols tested:",len(hits))

print("\n== isomorph bijection tests (10-windows with >=2 internal repeats, same repeat pattern at two places)")
def pattern(w):
    f={}; return tuple(f.setdefault(x,i) for i,x in enumerate(w))
def digs(x): return (x//25,(x//5)%5,x%5)
L=10; occ=collections.defaultdict(list)
for nm,v in m.items():
    for t in range(len(v)-L+1):
        w=v[t:t+L]
        if len(set(w))<=L-2: occ[pattern(w)].append((nm,t))
pairs=[(a,b) for l in occ.values() for a,b in itertools.combinations(l,2) if not (a[0]==b[0] and abs(a[1]-b[1])<L)]
aff=dig=ident=0
for (m1,t1),(m2,t2) in pairs:
    w1=m[m1][t1:t1+L]; w2=m[m2][t2:t2+L]; mp=dict(zip(w1,w2)); xs=list(mp)
    if w1==w2: ident+=1; continue
    x0,x1=xs[0],xs[1]; a=(mp[x1]-mp[x0])*pow((x1-x0)%N,N-2,N)%N; b=(mp[x0]-a*x0)%N
    aff+=all((a*x+b)%N==mp[x] for x in xs)
    ok=True
    for i in range(3):
        f={}
        for x in xs:
            if f.setdefault(digs(x)[i],digs(mp[x])[i])!=digs(mp[x])[i]: ok=False
    dig+=ok
print(f"  window pairs {len(pairs)} (identical windows {ident}); affine-consistent {aff}; digit-wise-consistent {dig}")
rng=random.Random(1); h=0; T=20000
for _ in range(T):
    xs=rng.sample(range(N),8); ys=rng.sample(range(N),8); mp=dict(zip(xs,ys)); ok=True
    for i in range(3):
        f={}
        for x in xs:
            if f.setdefault(digs(x)[i],digs(mp[x])[i])!=digs(mp[x])[i]: ok=False
    h+=ok
print(f"  random-bijection digit-wise rate {h/T}")
