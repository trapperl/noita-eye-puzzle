import random, sys, collections, math, re
from fp import load_corpus, dist_table, load_eyes
from mech import LookupDeck, CutDeck, Chao, RandGAK, text_to_idx, N
from mech2 import SpacedLookup, ChaoCtOnly, evaluate
lang=sys.argv[1]; use_space=sys.argv[2]=='space'
txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,use_space)
fr=collections.Counter(idx); freqs=[fr[i] for i in range(A)]
TT=dist_table(list(load_eyes().values()),8); obs=[r[1] for r in TT]; exp=[r[2]/83 for r in TT]
def dev8(r):
    s=0
    for d in range(8):
        mu=max(exp[d]*r[d],1e-3); ll=obs[d]*math.log(mu)-mu; lls=(obs[d]*math.log(obs[d])-obs[d]) if obs[d]>0 else 0
        s+=2*(lls-ll)
    return s
rs={}
for line in open(f"../results/rs_{lang}_{'space' if use_space else 'nospace'}.txt"):
    m=re.match(r'(.*?)\s+4-letter change: \[(.*?)\]\s+1-letter change: \[(.*?)\]',line)
    if m: rs[m.group(1).strip()]=([float(x) for x in m.group(2).split(',')],[float(x) for x in m.group(3).split(',')])
cands={}
for op in ['cut_then_depth','move_depth','move_rel','swap_rel']:
    for k in [4,8,11,14,17,20,23,26,32,40]:
        for sp in [1,2,3,4]: cands[f"{op} k={k} sp={sp}"]=lambda r,op=op,k=k,sp=sp:SpacedLookup(A,r,op,k,sp)
        cands[f"{op} k={k} random"]=lambda r,op=op,k=k:LookupDeck(A,r,op,k,'random')
for k in [4,15,19,23]: cands[f"CutDeck k={k}"]=lambda r,k=k:CutDeck(A,r,k,'random')
for nad in [4,20,41]:
    cands[f"Chao nadir={nad}"]=lambda r,nad=nad:Chao(A,r,nad,1,2,1,freqs)
    cands[f"ChaoCtOnly nadir={nad} ext=1"]=lambda r,nad=nad:ChaoCtOnly(A,r,nad,1,freqs)
cands["RandGAK"]=lambda r:RandGAK(A,r)
rows=[]
for name,mk in cands.items():
    chi,acc=evaluate(mk,idx,nkeys=2,nsym=15000); d=dev8(acc); p4,p1=rs.get(name,([9,9,9],[9,9,9]))
    # resync target: next20 after 4-letter change ~0.55 (E4/E5); penalise distance from it
    rows.append((d + 40*(p4[1]-0.55)**2, d, name, [round(x,2) for x in acc[:6]], p4, p1))
rows.sort()
print(f"lang={lang} space={use_space}; TARGET dist d1-6 = [0.00,0.41,0.74,2.16,0.92,1.01]; resync next20 ~0.55")
print(f"{'joint':>6} {'dev8':>5}  mechanism                    d1..d6                          resync4 (chg,+20,+40)  resync1")
for j,d,name,acc,p4,p1 in rows[:30]: print(f"{j:6.1f} {d:5.1f}  {name:28s} {acc}  {p4}  {p1}")
