# Acrescenta a indicadores_linhas.csv: pontos de parada (paradas da mesma linha a menos de 100 m contam como um ponto)
# e moradores por ponto de parada (pop_400m_a_pe ÷ pontos). Rodar depois de ind_monta.py.
import sys, os, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
G_,DST=sys.argv[1:3]; R=100.0
LAT0,LON0=-22.9,-43.45; KX=np.cos(np.radians(LAT0))*111320; KY=110574
def pontos(pts):
    n=len(pts)
    if n==0: return 0
    pr=cKDTree(pts).query_pairs(R,output_type='ndarray')
    g=coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(n,n)) if len(pr) else coo_matrix((n,n))
    return int(connected_components(g,directed=False)[0])
st=pd.read_csv(os.path.join(G_,'stops.txt'),dtype=str,keep_default_na=False); st=st[st.location_type!='1']
st['x']=((st.stop_lon.astype(float)-LON0)*KX).round(); st['y']=((st.stop_lat.astype(float)-LAT0)*KY).round(); st=st.set_index('stop_id')  # metros inteiros, como no painel
tr=pd.read_csv(os.path.join(G_,'trips.txt'),dtype=str)
stt=pd.read_csv(os.path.join(G_,'stop_times.txt'),dtype={'trip_id':str,'stop_id':str},usecols=['trip_id','stop_id'])
rs=stt.merge(tr[['trip_id','route_id']]).drop_duplicates(['route_id','stop_id'])
rs=rs[rs.stop_id.isin(st.index)]
NP={r:pontos(st.loc[g.stop_id,['x','y']].values) for r,g in rs.groupby('route_id')}
f=os.path.join(DST,'indicadores_linhas.csv'); X=pd.read_csv(f,dtype={'route_id':str,'linha':str})
X['n_pontos_parada']=X.route_id.map(NP).fillna(0).astype(int)
X['moradores_por_ponto_parada']=(X.pop_400m_a_pe/X.n_pontos_parada.replace(0,np.nan)).round(0)
c=list(X.columns); [c.remove(k) for k in ['n_pontos_parada','moradores_por_ponto_parada']]; i=c.index('pop_800m_a_pe')+1
X=X[c[:i]+['n_pontos_parada','moradores_por_ponto_parada']+c[i:]]
X.to_csv(f,index=False); print(X[['n_pontos_parada','moradores_por_ponto_parada']].describe().round(0).T)
