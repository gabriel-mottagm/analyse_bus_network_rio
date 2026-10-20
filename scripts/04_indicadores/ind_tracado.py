# Indicadores de traçado por linha: extensão, velocidade, tortuosidade, divergência ida/volta
import sys, os, numpy as np, pandas as pd
from scipy.spatial import cKDTree
G_,OUT,DST=sys.argv[1:4]
LAT0,LON0=-22.9,-43.45; KX=np.cos(np.radians(LAT0))*111320; KY=110574
sh=pd.read_csv(os.path.join(G_,'shapes.txt'),dtype={'shape_id':str}).sort_values(['shape_id','shape_pt_sequence'])
sh['x']=(sh.shape_pt_lon-LON0)*KX; sh['y']=(sh.shape_pt_lat-LAT0)*KY
SH={k:g[['x','y']].values for k,g in sh.groupby('shape_id')}
def length(a): return np.hypot(*np.diff(a,axis=0).T).sum()
def dens(a,step=10):
    out=[a[:1]]
    for p,q in zip(a[:-1],a[1:]):
        n=max(1,int(np.hypot(*(q-p))//step)); t=np.arange(1,n+1)[:,None]/n; out.append(p+t*(q-p))
    return np.vstack(out)
P=pd.read_csv(os.path.join(OUT,'partidas_expandidas.csv'),usecols=['route_id','direction_id','shape_id','duracao_min'],dtype={'route_id':str,'shape_id':str})
rows=[]
for rid,g in P.groupby('route_id'):
    dirs={}
    for d,gd in g.groupby('direction_id'):
        s=gd.shape_id.value_counts().index[0]; a=SH[s]; L=length(a)
        dur=gd[gd.shape_id==s].duracao_min.median()
        reta=np.hypot(*(a[-1]-a[0]))
        dirs[d]=dict(shape=s,a=a,L=L,dur=dur,reta=reta)
    Ls=[v['L'] for v in dirs.values()]
    vel=np.mean([v['L']/1000/(v['dur']/60) for v in dirs.values() if v['dur']>0])
    circ=all(v['reta']<500 for v in dirs.values())
    tort=np.nan if circ else round(np.mean([v['L']/max(v['reta'],1) for v in dirs.values()]),2)
    div=np.nan
    if len(dirs)==2:
        a0,a1=dens(dirs[0]['a']),dens(dirs[1]['a'])
        d01,_=cKDTree(a1).query(a0); d10,_=cKDTree(a0).query(a1)
        un=(d01>40).mean()*dirs[0]['L']+(d10>40).mean()*dirs[1]['L']
        div=round(100*un/(dirs[0]['L']+dirs[1]['L']),1)
    rows.append({'route_id':rid,'n_sentidos':len(dirs),'circular':circ,'extensao_km':round(np.mean(Ls)/1000,2),
                 'velocidade_comercial_kmh':round(vel,1),'tortuosidade':tort,'divergencia_ida_volta_pct':div})
T=pd.DataFrame(rows); T.to_csv(os.path.join(DST,'_tracado.csv'),index=False)
print(T.describe().round(2).T); print('circulares:',T.circular.sum(),' 1 sentido:',(T.n_sentidos==1).sum())
