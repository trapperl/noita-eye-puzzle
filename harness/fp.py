import csv, collections, math, re, unicodedata, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_eyes():
    rows=list(csv.reader(open(ROOT+'/data/noita_eye_data_trigrams.csv')))
    return {r[1]:[int(x) for x in r[2:] if x!=''] for r in rows[1:]}
def dist_table(seqs, dmax=40, n=83):
    out=[]
    for d in range(1,dmax+1):
        e=c=0
        for v in seqs:
            for t in range(len(v)-d): c+=1; e+=v[t]==v[t+d]
        exp=c/n; z=(e-exp)/math.sqrt(exp*(1-1/n)) if exp>0 else 0
        out.append((d,e,c,e/c*n if c else 0,z))
    return out
def ioc(seqs,n=83):
    allv=[x for v in seqs for x in v]; c=collections.Counter(allv); N=len(allv)
    return sum(k*(k-1) for k in c.values())/(N*(N-1))*n
def fingerprint(seqs,dmax=12):
    t=dist_table(seqs,dmax); return [round(r[3],2) for r in t]
def load_corpus(lang):
    files={'en':['corpus/The-Adventures-of-Sherlock-Holmes_1661/1661-8.txt','corpus/Alice-s-Adventures-in-Wonderland_11/11-0.txt'],
           'fi':['corpus/Kalevala_7000/7000-8.txt']}[lang]
    txt=''
    for f in files:
        raw=open(ROOT+'/'+f,'rb').read()
        try: s=raw.decode('utf-8')
        except UnicodeDecodeError: s=raw.decode('latin-1')
        # strip gutenberg header/footer roughly
        a=s.find('*** START'); b=s.find('*** END'); s=s[a+1000 if a>0 else 0: b if b>0 else len(s)]
        txt+=s
    txt=txt.lower()
    if lang=='en':
        txt=unicodedata.normalize('NFKD',txt).encode('ascii','ignore').decode()
        alpha='abcdefghijklmnopqrstuvwxyz'
    else:
        alpha='abcdefghijklmnopqrstuvwxyzäö'
    txt=re.sub(r'\s+',' ',txt)
    return ''.join(ch for ch in txt if ch in alpha or ch==' '), alpha
if __name__=='__main__':
    m=load_eyes(); seqs=list(m.values())
    print("IoC ratio",round(ioc(seqs),3))
    for d,e,c,r,z in dist_table(seqs,40): print(f"d={d:2d} obs={e:3d} exp={c/83:5.1f} ratio={r:4.2f} z={z:+5.2f}"+(" <<" if abs(z)>2.5 else ""))
    for lang in ['en','fi']:
        t,a=load_corpus(lang); print(lang,len(t),t[:80])
