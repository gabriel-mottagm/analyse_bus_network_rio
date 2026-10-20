import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
g=np.load('osm/grafo.npz'); X,Y,iu,iv,L,ea,lab=[g[k] for k in ['X','Y','iu','iv','L','ea','lab']]
N=len(X); G=coo_matrix((np.maximum(L,0.01),(iu,iv)),shape=(N,N)).tocsr(); G=G.maximum(G.T)
deg=np.bincount(np.concatenate([iu,iv]),minlength=N)
LAT0,LON0=-22.9,-43.45; KX=np.cos(np.radians(LAT0))*111320; KY=110574
st=pd.read_csv('gtfs/stops.txt',dtype=str,keep_default_na=False)
st['x']=(st.stop_lon.astype(float)-LON0)*KX; st['y']=(st.stop_lat.astype(float)-LAT0)*KY
c=st[st.stop_name.str.contains('Copacabana|Barata Ribeiro|Siqueira Campos|Santa Clara|Figueiredo',regex=True)&(st.stop_lat.astype(float).between(-22.985,-22.965))].head(6)
T=cKDTree(np.column_stack([X,Y]))
for _,s in c.iterrows():
    d,j=T.query([s.x,s.y]); dd=dijkstra(G,directed=False,indices=j,limit=1500)
    near=T.query_ball_point([s.x,s.y],300); near=np.array(near)
    eu=np.hypot(X[near]-s.x,Y[near]-s.y); m=eu>100
    rat=dd[near][m]/eu[m]
    # nó alocável (rua) mais próximo vs nó escolhido
    alloc_nodes=np.unique(np.concatenate([iu[ea],iv[ea]])); isal=np.isin(j,alloc_nodes)
    print(f"{s.stop_name[:40]:40s} snap {d:4.0f}m grau {deg[j]} rua? {isal}  razão mediana {np.median(rat):.2f}  p90 {np.percentile(rat,90):.2f}  inalcançáveis {np.isinf(dd[near]).mean()*100:.0f}%")
print('--- pares de paradas (rede / linha reta)')
c=c.reset_index(drop=True); js=[T.query([s.x,s.y])[1] for _,s in c.iterrows()]
D=dijkstra(G,directed=False,indices=js)
for a in range(len(c)):
    for b in range(a+1,len(c)):
        e=np.hypot(c.x[a]-c.x[b],c.y[a]-c.y[b])
        if e>150: print(f"{c.stop_name[a][:28]:28s} -> {c.stop_name[b][:28]:28s} reta {e:5.0f} rede {D[a,js[b]]:5.0f} razão {D[a,js[b]]/e:.2f}")
