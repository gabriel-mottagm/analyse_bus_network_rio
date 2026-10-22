# População a até 400 m a pé de cada linha, com perfil de renda e cor/raça
import sys, os, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
G_,C,OS,APE,DST=sys.argv[1:6]; R=400
g=np.load(os.path.join(OS,'grafo.npz')); X,Y,iu,iv,L,lab,main=[g[k] for k in ['X','Y','iu','iv','L','lab','main']]; main=int(main)
p=np.load(os.path.join(OS,'pontos.npz')); px,py,pu,pv,pt,pL,onm,snap,off=[p[k] for k in ['x','y','u','v','t','L','onmain','snap','off']]
LAT0,LON0=-22.9,-43.45; KX=np.cos(np.radians(LAT0))*111320; KY=110574
def r(n,**k): return pd.read_csv(os.path.join(G_,n+'.txt'),keep_default_na=False,**k)
st=r('stops',dtype=str); tr=r('trips',dtype=str); stt=r('stop_times',dtype={'trip_id':str,'stop_id':str},usecols=['trip_id','stop_id'])
st=st[st.location_type!='1'].copy().reset_index(drop=True)
st['x']=(st.stop_lon.astype(float)-LON0)*KX; st['y']=(st.stop_lat.astype(float)-LAT0)*KY
N=len(X); mn=np.where(lab==main)[0]; dsn,j=cKDTree(np.column_stack([X[mn],Y[mn]])).query(st[['x','y']].values)
st['node']=N+np.arange(len(st)); st['snap']=mn[j]; NN=N+len(st)
G=coo_matrix((np.maximum(np.concatenate([L,dsn]),0.01),(np.concatenate([iu,st.node]),np.concatenate([iv,st.snap]))),shape=(NN,NN)).tocsr(); G=G.maximum(G.T)
sid=dict(zip(st.stop_id,st.node))
def pdist(dn):
    d=np.full(len(px),np.inf); m=onm; d[m]=np.minimum(dn[pu[m]]+pt[m]*pL[m],dn[pv[m]]+(1-pt[m])*pL[m]); m=~onm; d[m]=dn[snap[m]]+off[m]; return d
# pares ponto-setor com atributos
ps=pd.read_csv(os.path.join(OS,'pontos_setores.csv.gz'))
S=pd.read_csv(os.path.join(APE,'setores_cobertura_a_pe.csv'))
Sp=S[(S.populacao>0)&(S.renda_media_responsavel>0)].sort_values('renda_media_responsavel')
dec=pd.Series(-1,index=S.index); dec[Sp.index]=np.minimum((Sp.populacao.cumsum()/Sp.populacao.sum()*10).astype(int)+1,10)
pp=ps.p.values; pop=ps['pop'].values; ss=ps.s.values
rbaixa=pop*((dec.values[ss]>=1)&(dec.values[ss]<=3)); ralta=pop*(dec.values[ss]>=8)
share=lambda c:(S[c]/S.populacao.replace(0,np.nan)).fillna(0).values
pn=pop*(share('preta')+share('parda'))[ss]; renda=pop*np.where(S.renda_media_responsavel.values[ss]>0,S.renda_media_responsavel.values[ss],0); rpop=pop*(S.renda_media_responsavel.values[ss]>0)
rs=stt.merge(tr[['trip_id','route_id']]).drop_duplicates(['stop_id','route_id']); rs=rs[rs.stop_id.isin(sid)]
rows=[]
for rid,grp in rs.groupby('route_id'):
    dd=pdist(dijkstra(G,directed=False,indices=[sid[s] for s in grp.stop_id.unique()],min_only=True,limit=801))
    cov=(dd<=R)[pp]; P_=pop[cov].sum(); P8=pop[(dd<=800)[pp]].sum()
    rows.append({'route_id':rid,'pop_400m_a_pe':round(P_),'pop_800m_a_pe':round(P8),'pct_pop_30pct_renda_mais_baixa':round(100*rbaixa[cov].sum()/P_,1) if P_>0 else np.nan,
                 'pct_pop_30pct_renda_mais_alta':round(100*ralta[cov].sum()/P_,1) if P_>0 else np.nan,
                 'pct_pretos_pardos':round(100*pn[cov].sum()/P_,1) if P_>0 else np.nan,
                 'renda_media_area_atendida':round(renda[cov].sum()/max(rpop[cov].sum(),1),0)})
D=pd.DataFrame(rows); D.to_csv(os.path.join(DST,'_pop_linha.csv'),index=False); print(D.describe().round(1).T)
