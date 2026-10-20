# 2) Distribui a população de cada setor ao longo das vias (pontos a cada ~20 m), com fallback uniforme
import sys, os, numpy as np, pandas as pd
from scipy.spatial import cKDTree
C,OS=sys.argv[1],sys.argv[2]; STEP=20.0
g=np.load(os.path.join(OS,'grafo.npz')); X,Y,iu,iv,L,ea,lab,main=[g[k] for k in ['X','Y','iu','iv','L','ea','lab','main']]; main=int(main)
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL=z['meta'][:5]; nx,ny=int(nx),int(ny)
own=np.full(nx*ny,-1,dtype=np.int32); own[z['cell_idx']]=z['cell_own']
S=pd.read_csv(os.path.join(C,'setores_atributos.csv')); pop=S.total_de_p.values.astype(float)
# amostras nas arestas alocáveis
e=np.where(ea&(L>0.5))[0]; n=np.maximum(1,np.ceil(L[e]/STEP)).astype(int)
E=np.repeat(e,n); k=np.concatenate([np.arange(m) for m in n]); nn=np.repeat(n,n)
t=(k+0.5)/nn; w=L[E]/nn
px=X[iu[E]]+t*(X[iv[E]]-X[iu[E]]); py=Y[iu[E]]+t*(Y[iv[E]]-Y[iu[E]])
print(f"pontos nas vias: {len(px):,}")
# setores vizinhos (janela 3x3 de células de 20 m ≈ ±30 m)
cx=((px-x0)//CELL).astype(int); cy=((py-y0)//CELL).astype(int)
pi_l=[];si_l=[]
for dx in (-1,0,1):
    for dy in (-1,0,1):
        xx=np.clip(cx+dx,0,nx-1); yy=np.clip(cy+dy,0,ny-1); o=own[yy*nx+xx]; m=o>=0
        pi_l.append(np.where(m)[0]); si_l.append(o[m])
P=pd.DataFrame({'p':np.concatenate(pi_l),'s':np.concatenate(si_l)}).drop_duplicates()
P['w']=w[P.p.values]
ws=P.groupby('s').w.sum(); P['pop']=pop[P.s.values]*P.w.values/ws.reindex(P.s.values).values
P=P[P['pop']>0]
sem=np.setdiff1d(np.where(pop>0)[0],P.s.unique())
print(f"setores com moradores: {(pop>0).sum():,}; sem via próxima (fallback uniforme): {len(sem)} ({pop[sem].sum():,.0f} hab, {pop[sem].sum()/pop.sum()*100:.1f}%)")
# fallback: células da grade
ci,co,cp=z['cell_idx'],z['cell_own'],z['cell_pop']; m=np.isin(co,sem)&(cp>0)
fx=x0+(ci[m]%nx+0.5)*CELL; fy=y0+(ci[m]//nx+0.5)*CELL
nf=m.sum(); base=len(px)
F=pd.DataFrame({'p':base+np.arange(nf),'s':co[m],'w':0.0,'pop':cp[m]})
P=pd.concat([P,F],ignore_index=True)
# atributos dos pontos: tipo 0 = na aresta do componente principal (distância exata pela rede);
# tipo 1 = fora da rede principal ou célula de fallback (liga ao nó mais próximo da rede principal + linha reta)
allx=np.concatenate([px,fx]); ally=np.concatenate([py,fy])
eu_=np.concatenate([iu[E],np.full(nf,-1)]); ev_=np.concatenate([iv[E],np.full(nf,-1)])
tt=np.concatenate([t,np.zeros(nf)]); LL=np.concatenate([L[E],np.zeros(nf)])
onmain=np.concatenate([lab[iu[E]]==main,np.zeros(nf,bool)])
mainnodes=np.where(lab==main)[0]; T=cKDTree(np.column_stack([X[mainnodes],Y[mainnodes]]))
off=np.zeros(len(allx)); snap=np.full(len(allx),-1)
q=~onmain; d,j=T.query(np.column_stack([allx[q],ally[q]])); off[q]=d; snap[q]=mainnodes[j]
ppop=np.bincount(P.p.values,weights=P['pop'].values,minlength=len(allx))
print(f"população alocada: {ppop.sum():,.0f} (original {pop.sum():,.0f}); em pontos fora da rede principal: {ppop[q].sum():,.0f}; offset mediano desses: {np.median(off[q][ppop[q]>0]):.0f} m")
np.savez_compressed(os.path.join(OS,'pontos.npz'),x=allx,y=ally,u=eu_,v=ev_,t=tt,L=LL,onmain=onmain,snap=snap,off=off,pop=ppop)
P[['p','s','pop']].to_csv(os.path.join(OS,'pontos_setores.csv.gz'),index=False)
