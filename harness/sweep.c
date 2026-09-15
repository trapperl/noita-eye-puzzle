/* Sweep of the non-rotating move-to-depth deck over arithmetic-progression slot layouts.
   Mechanism: c = deck[slot[p]]; remove c; insert at depth k.  Layout: slot[letter j] = (a + s*rank(j)) mod 83,
   rank = alphabetical (mode 0) or frequency order (mode 1).  For each config, NKEYS random decks x NSYM symbols;
   prints k a s mode dev8 r1..r8 and the spread of r4 across keys.
   Usage: ./sweep corpus.idx corpus.meta target.txt */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define N 83
#define NKEYS 3
#define NSYM 12000
static unsigned long long rs=88172645463325252ULL;
static unsigned long long xr(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long L=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*idx=malloc(L); fread(idx,1,L,f); fclose(f);
  int A,order[64]; f=fopen(argv[2],"r"); fscanf(f,"%d",&A); for(int i=0;i<A;i++)fscanf(f,"%d",&order[i]); fclose(f);
  int obs[8]; double ex[8]; f=fopen(argv[3],"r"); for(int d=0;d<8;d++)fscanf(f,"%d %lf",&obs[d],&ex[d]); fclose(f);
  double lls[8]; for(int d=0;d<8;d++) lls[d]=obs[d]>0? obs[d]*log((double)obs[d])-obs[d]:0;
  int rank_alpha[64],rank_freq[64]; for(int j=0;j<A;j++){rank_alpha[j]=j;} for(int i=0;i<A;i++)rank_freq[order[i]]=i;
  unsigned char deck[N],seq[NSYM];
  for(int mode=0;mode<2;mode++) for(int s=1;s<=41;s++) for(int a=0;a<N;a++) for(int k=0;k<N;k++){
    int slot[64]; int*rk=mode?rank_freq:rank_alpha; int ok=1;
    for(int j=0;j<A;j++){slot[j]=(a+s*rk[j])%N;}
    /* slots must be distinct */
    { int seen[N]={0}; for(int j=0;j<A;j++){ if(seen[slot[j]]){ok=0;break;} seen[slot[j]]=1; } }
    if(!ok) continue;
    double acc[8]={0}; double r4min=9,r4max=-9;
    for(int key=0;key<NKEYS;key++){
      for(int i=0;i<N;i++)deck[i]=i;
      for(int i=N-1;i>0;i--){int j=xr()%(i+1);unsigned char t=deck[i];deck[i]=deck[j];deck[j]=t;}
      long st=xr()%(L-NSYM);
      for(int t=0;t<NSYM;t++){
        int i=slot[idx[st+t]]; unsigned char c=deck[i];
        if(i<k){ memmove(deck+i,deck+i+1,k-i); deck[k]=c; }
        else if(i>k){ memmove(deck+k+1,deck+k,i-k); deck[k]=c; }
        seq[t]=c;
      }
      for(int d=1;d<=8;d++){ int e=0; for(int t=0;t<NSYM-d;t++) e+= seq[t]==seq[t+d]; double r=(double)e/(NSYM-d)*N; acc[d-1]+=r/NKEYS; if(d==4){if(r<r4min)r4min=r; if(r>r4max)r4max=r;} }
    }
    double dev=0; for(int d=0;d<8;d++){ double mu=ex[d]*acc[d]; if(mu<1e-3)mu=1e-3; dev+=2*(lls[d]-(obs[d]*log(mu)-mu)); }
    printf("%d %d %d %d %.2f %.2f",k,a,s,mode,dev,r4max-r4min); for(int d=0;d<8;d++)printf(" %.2f",acc[d]); printf("\n");
  }
  return 0;
}
