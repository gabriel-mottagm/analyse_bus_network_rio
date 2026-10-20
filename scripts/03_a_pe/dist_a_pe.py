# 3) Distância a pé até as paradas (Dijkstra multi-origem) e nível de serviço por ponto
import sys, os, time, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
G_,C,OS,OUT,OUTP=sys.argv[1:6]   # gtfs, censo, osm, cob (linha reta, p/ comparação), saída
PART=sys.argv[6] if len(sys.argv)>6 else 'out'   # pasta de partidas_expandidas.csv
t0=time.time()
g=np.load(os.path.join(OS,'grafo.npz')); X,Y,iu,iv,L,lab,main=[g[k] for k in ['X','Y','iu','iv','L','lab','main']]; main=int(main)
p=np.load(os.path.join(OS,'pontos.npz')); px,py,pu,pv,pt,pL,onm,snap,off,ppop=[p[k] for k in ['x','y','u','v','t','L','onmain','snap','off','pop']]
z=np.load(os.path.join(C,'grade.npz')); LAT0,LON0,KX,KY=z['meta'][5:9]
def r(n,**k): return pd.read_csv(os.path.join(G_,n+'.txt'),keep_default_na=False,**k)
st=r('stops',dtype=str); ro=r('routes',dtype=str); tr=r('trips',dtype=str)
stt=r('stop_times',dtype={'trip_id':str,'stop_id':str},usecols=['trip_id','stop_id'])
st=st[st.location_type!='1'].copy().reset_index(drop=True)
st['x']=(st.stop_lon.astype(float)-LON0)*KX; st['y']=(st.stop_lat.astype(float)-LAT0)*KY
# paradas viram nós extras ligados ao nó mais próximo da rede principal
N=len(X); mainnodes=np.where(lab==main)[0]; T=cKDTree(np.column_stack([X[mainnodes],Y[mainnodes]]))
dsn,j=T.query(st[['x','y']].values); st['node']=N+np.arange(len(st)); st['snap']=mainnodes[j]; st['snap_m']=dsn
print(f"paradas: {len(st)}; distância parada→rede: mediana {np.median(dsn):.0f} m, p95 {np.percentile(dsn,95):.0f} m, >100 m: {(dsn>100).sum()}")
NN=N+len(st)
rows=np.concatenate([iu,st.node.values]); cols=np.concatenate([iv,st.snap.values]); w=np.concatenate([L,np.maximum(dsn,0.01)])
G=coo_matrix((np.maximum(w,0.01),(rows,cols)),shape=(NN,NN)).tocsr(); G=G.minimum(G.T) if False else G.maximum(G.T)
sid=dict(zip(st.stop_id,st.node))
def pdist(dn):
    """distância a pé de cada ponto dado o vetor de distâncias por nó"""
    d=np.full(len(px),np.inf)
    m=onm; d[m]=np.minimum(dn[pu[m]]+pt[m]*pL[m], dn[pv[m]]+(1-pt[m])*pL[m])
    m=~onm; d[m]=dn[snap[m]]+off[m]
    return d
dn=dijkstra(G,directed=False,indices=st.node.values,min_only=True,limit=5000)
dw=pdist(dn)
de,_=cKDTree(st[['x','y']].values).query(np.column_stack([px,py]))
TOT=ppop.sum()
print(f"Dijkstra global: {time.time()-t0:.0f}s")
brt=set(ro.route_id[ro.route_type=='702'])
rs=stt.merge(tr[['trip_id','route_id','direction_id']]).drop_duplicates(['stop_id','route_id','direction_id'])
rs=rs[rs.stop_id.isin(sid)]
brt_nodes=[sid[s] for s in rs[rs.route_id.isin(brt)].stop_id.unique()]
dwb=pdist(dijkstra(G,directed=False,indices=brt_nodes,min_only=True,limit=5000))
rede=[]
for R in [200,300,400,500,800,1000]:
    rede.append({'raio_m':R,'pop_a_pe':round(ppop[dw<=R].sum()),'pct_a_pe':round(100*ppop[dw<=R].sum()/TOT,1),
                 'pop_linha_reta':round(ppop[de<=R].sum()),'pct_linha_reta':round(100*ppop[de<=R].sum()/TOT,1),
                 'pct_brt_a_pe':round(100*ppop[dwb<=R].sum()/TOT,1)})
rede=pd.DataFrame(rede); print(rede.to_string(index=False)); rede.to_csv(os.path.join(OUTP,'cobertura_rede_a_pe.csv'),index=False)
# frequência no pico por linha-sentido
P=pd.read_csv(os.path.join(PART,'partidas_expandidas.csv'),usecols=['service_id','route_id','direction_id','hora_partida'],dtype={'route_id':str})
hh=P.hora_partida.str[:2].astype(int)
pk=P[(P.service_id=='U_REG')&(hh>=6)&(hh<9)].groupby(['route_id','direction_id']).size()/3.0
dia=P[P.service_id=='U_REG'].groupby('route_id').size()
R=400; freq=np.zeros(len(px)); nlin=np.zeros(len(px),dtype=np.int16); linhas=[]
for rid,grp in rs.groupby('route_id'):
    best=np.zeros(len(px)); anyc=np.zeros(len(px),bool)
    for dirc,g2 in grp.groupby('direction_id'):
        nodes=[sid[s] for s in g2.stop_id.unique()]
        dd=pdist(dijkstra(G,directed=False,indices=nodes,min_only=True,limit=R+1))
        c=dd<=R; anyc|=c; f=pk.get((rid,int(dirc)),0.0)
        best=np.where(c,np.maximum(best,f),best)
    freq+=best; nlin+=anyc
    linhas.append({'route_id':rid,'pop_400m_a_pe':round(ppop[anyc].sum()),'n_paradas':grp.stop_id.nunique(),'partidas_dia_util':int(dia.get(rid,0)),
                   'onibus_h_pico_ambos_sentidos':round(pk.get((rid,0),0)+pk.get((rid,1),0),1)})
print(f"linhas: {time.time()-t0:.0f}s")
Lr=pd.DataFrame(linhas).merge(ro[['route_id','agency_id','route_short_name','route_long_name','route_type']])
ag=r('agency',dtype=str).set_index('agency_id').agency_name; Lr['operador']=Lr.agency_id.map(ag)
Lr['modo']=Lr.route_type.map({'700':'Ônibus','702':'BRT','200':'Executivo'})
old=pd.read_csv(os.path.join(OUT,'linhas_populacao.csv'),dtype={'route_id':str})[['route_id','pop_400m']].rename(columns={'pop_400m':'pop_400m_linha_reta'})
Lr=Lr.merge(old,how='left'); Lr['variacao_pct']=(100*(Lr.pop_400m_a_pe/Lr.pop_400m_linha_reta-1)).round(1)
Lr=Lr[['route_id','route_short_name','route_long_name','operador','modo','n_paradas','partidas_dia_util','onibus_h_pico_ambos_sentidos','pop_400m_a_pe','pop_400m_linha_reta','variacao_pct']].sort_values('pop_400m_a_pe',ascending=False)
Lr.to_csv(os.path.join(OUTP,'linhas_populacao_a_pe.csv'),index=False)
print(Lr.variacao_pct.describe().round(1).to_dict())
# por parada (população a até 400 m a pé)
PT=cKDTree(np.column_stack([px,py])); popst=[]
for i,row in st.iterrows():
    cand=np.array(PT.query_ball_point([row.x,row.y],R),dtype=np.int64)
    if len(cand)==0: popst.append(0); continue
    dd=dijkstra(G,directed=False,indices=int(row.node),limit=R+1)
    m=onm[cand]; dc=np.full(len(cand),np.inf)
    cm=cand[m]; dc[m]=np.minimum(dd[pu[cm]]+pt[cm]*pL[cm],dd[pv[cm]]+(1-pt[cm])*pL[cm])
    cn=cand[~m]; dc[~m]=dd[snap[cn]]+off[cn]
    popst.append(round(ppop[cand[dc<=R]].sum()))
st['pop_400m_a_pe']=popst
print(f"paradas: {time.time()-t0:.0f}s")
rp=pd.read_csv(os.path.join(OUT,'paradas_populacao.csv'),dtype={'stop_id':str}).set_index('stop_id')
PS=rp.join(st.set_index('stop_id')[['pop_400m_a_pe','snap_m']]).rename(columns={'pop_400m':'pop_400m_linha_reta','snap_m':'dist_parada_rede_m'})
PS.reset_index().to_csv(os.path.join(OUTP,'paradas_populacao_a_pe.csv'),index=False)
np.savez_compressed(os.path.join(OUTP,'pontos_resultado.npz'),dw=dw,de=de,dwb=dwb,freq=freq,nlin=nlin)
print(f"total: {time.time()-t0:.0f}s")
