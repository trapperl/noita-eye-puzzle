"""CP-SAT key search for the non-rotating move-to-depth deck.
Mechanism: c = deck[slot[p]]; remove c; insert at depth k.  Unknowns: initial deck (shared by all messages),
slot set S (|S| <= SMAX), with k given.  Constraint: decrypting every message from the initial deck visits only slot positions.
Modes:
  synth <lang> <k> <a> <s> <nmsg> <len> <timeout_s>   encipher random text segments with a random deck and AP layout, then solve
  real <k> <timeout_s>                                 solve on the eye data (positions 2.. of every message)
"""
import sys, random, time, collections
from ortools.sat.python import cp_model
from fp import load_eyes, load_corpus
from mech import text_to_idx
N=83
def encipher(deck,slot,k,seg):
    d=list(deck); out=[]
    for p in seg:
        i=slot[p]; c=d.pop(i); d.insert(k,c); out.append(c)
    return out
def build(msgs,k,smax,hint=None):
    m=cp_model.CpModel()
    pos0=[m.NewIntVar(0,N-1,f"p0_{x}") for x in range(N)]
    m.AddAllDifferent(pos0)
    isslot=[m.NewBoolVar(f"slot_{q}") for q in range(N)]
    m.Add(sum(isslot)<=smax)
    nsteps=0
    for mi,msg in enumerate(msgs):
        pos=list(pos0)
        for t,c in enumerate(msg):
            i=pos[c]
            # i must be a slot
            b=m.NewBoolVar(f"s_{mi}_{t}"); m.AddElement(i,isslot,b); m.Add(b==1)
            newpos=[None]*N
            for x in range(N):
                if x==c:
                    newpos[x]=m.NewConstant(k); continue
                px=pos[x]
                above=m.NewBoolVar(f"a_{mi}_{t}_{x}")      # px > i
                m.Add(px>i).OnlyEnforceIf(above); m.Add(px<i).OnlyEnforceIf(above.Not())
                ge=m.NewBoolVar(f"g_{mi}_{t}_{x}")         # (px - above) >= k
                m.Add(px-above>=k).OnlyEnforceIf(ge); m.Add(px-above<=k-1).OnlyEnforceIf(ge.Not())
                np_=m.NewIntVar(0,N-1,f"p_{mi}_{t+1}_{x}")
                m.Add(np_==px-above+ge)
                newpos[x]=np_
            pos=newpos; nsteps+=1
    return m,pos0,isslot,nsteps
def solve(msgs,k,smax,timeout,workers=4,truth=None):
    t0=time.time(); m,pos0,isslot,nsteps=build(msgs,k,smax)
    print(f"model built: {nsteps} steps, {time.time()-t0:.1f}s",flush=True)
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=timeout; s.parameters.num_workers=workers; s.parameters.log_search_progress=False
    r=s.Solve(m); print("status",s.StatusName(r),f"time {s.WallTime():.1f}s")
    if r in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        deck=[None]*N
        for x in range(N): deck[s.Value(pos0[x])]=x
        S=[q for q in range(N) if s.Value(isslot[q])]
        print("slots found:",S,"count",len(S))
        if truth:
            tdeck,tslots=truth; print("true slots:",sorted(set(tslots)))
            print("deck matches truth:",deck==tdeck)
        # verify by decrypting
        ok=True
        for msg in msgs:
            d=list(deck)
            for c in msg:
                i=d.index(c)
                if i not in S: ok=False
                d.pop(i); d.insert(k,c)
        print("decrypt visits only slots:",ok)
        return deck,S
    return None
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='synth':
        lang,k,a,sp,nmsg,L,timeout=sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]),float(sys.argv[8])
        txt,alpha=load_corpus(lang); idx,A=text_to_idx(txt,alpha,lang=='fi')
        rng=random.Random(5); deck=list(range(N)); rng.shuffle(deck); slot=[(a+sp*j)%N for j in range(A)]
        msgs=[]
        for j in range(nmsg):
            st=rng.randrange(0,len(idx)-L); msgs.append(encipher(deck,slot,k,idx[st:st+L]))
        print(f"synthetic: {nmsg} msgs x {L}, A={A}, k={k}, layout a={a} s={sp}; distinct symbols seen: {len(set(x for mm in msgs for x in mm))}")
        solve(msgs,k,A+1,timeout,truth=(deck,slot))
    else:
        k,timeout=int(sys.argv[2]),float(sys.argv[3])
        eyes=load_eyes(); msgs=[v[1:] for v in eyes.values()]
        print(f"real data: {len(msgs)} msgs, {sum(map(len,msgs))} symbols, k={k}")
        solve(msgs,k,30,timeout)
