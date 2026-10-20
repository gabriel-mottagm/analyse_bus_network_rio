import sys, os, json, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def pontos_parada(pts,r=100):
    n=len(pts)
    if n==0: return 0
    pr=cKDTree(pts).query_pairs(r,output_type='ndarray')
    g=coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(n,n)) if len(pr) else coo_matrix((n,n))
    return int(connected_components(g,directed=False)[0])
G_,OUT,LIN,DST=sys.argv[1:5]
LAT0,LON0=-22.9,-43.45; KX=np.cos(np.radians(LAT0))*111320; KY=110574
def rdp(a,eps):
    if len(a)<3: return a
    st=[(0,len(a)-1)]; keep=np.zeros(len(a),bool); keep[0]=keep[-1]=True
    while st:
        i,j=st.pop(); p,q=a[i],a[j]; seg=a[i+1:j]
        if len(seg)==0: continue
        d=q-p; n=np.hypot(*d); v=seg-p
        dist=np.abs(d[0]*v[:,1]-d[1]*v[:,0])/n if n>0 else np.hypot(v[:,0],v[:,1])
        k=np.argmax(dist)
        if dist[k]>eps: keep[i+1+k]=True; st+=[(i,i+1+k),(i+1+k,j)]
    return a[keep]
X=pd.read_csv(os.path.join(LIN,'indicadores_linhas.csv'),dtype={'route_id':str,'linha':str})
Fx=pd.read_csv(os.path.join(LIN,'linhas_intervalo_por_faixa.csv'),dtype={'route_id':str})
P=pd.read_csv(os.path.join(OUT,'partidas_expandidas.csv'),dtype={'route_id':str,'shape_id':str},usecols=['route_id','service_id','direction_id','shape_id','hora_partida','hora_do_dia'])
P['s']=P.hora_partida.str.split(':',expand=True).astype(int).pipe(lambda d:d[0]*3600+d[1]*60)
sh=pd.read_csv(os.path.join(G_,'shapes.txt'),dtype={'shape_id':str}).sort_values(['shape_id','shape_pt_sequence'])
sh['x']=(sh.shape_pt_lon-LON0)*KX; sh['y']=(sh.shape_pt_lat-LAT0)*KY
SH={k:g[['x','y']].values for k,g in sh.groupby('shape_id')}
st=pd.read_csv(os.path.join(G_,'stops.txt'),dtype=str,keep_default_na=False); st=st[st.location_type!='1'].reset_index(drop=True)
st['x']=((st.stop_lon.astype(float)-LON0)*KX).round().astype(int); st['y']=((st.stop_lat.astype(float)-LAT0)*KY).round().astype(int)
sidx={s:i for i,s in enumerate(st.stop_id)}
tr=pd.read_csv(os.path.join(G_,'trips.txt'),dtype=str); stt=pd.read_csv(os.path.join(G_,'stop_times.txt'),dtype={'trip_id':str,'stop_id':str},usecols=['trip_id','stop_id'])
rs=stt.merge(tr[['trip_id','route_id']]).drop_duplicates(['route_id','stop_id'])
RS={r:sorted(sidx[s] for s in g.stop_id if s in sidx) for r,g in rs.groupby('route_id')}
DIAS=['U_REG','S_REG','D_REG']
FAIXAS=['Madrugada (0h–5h)','Pico manhã (6h–9h)','Entrepico (9h–16h)','Pico tarde (16h–19h)','Noite (19h–24h)','Dia todo']
FI={(r.route_id,r.service_id,r.faixa):(r.intervalo_medio_min,r.partidas) for r in Fx.itertuples()}
H=P.groupby(['route_id','service_id','hora_do_dia']).size()
def hm(s): s=int(s)%86400; return f"{s//3600:02d}:{s%3600//60:02d}"
lines=[]
for i,r in X.reset_index(drop=True).iterrows():
    rid=r.route_id; g=P[P.route_id==rid]
    geom=[]
    for d,gd in g.groupby('direction_id'):
        a=rdp(SH[gd.shape_id.value_counts().index[0]],7); geom.append(np.round(a).astype(int).ravel().tolist())
    allp=np.vstack([np.array(gg).reshape(-1,2) for gg in geom])
    iv=[[None if not (rid,sv,f) in FI or pd.isna(FI[(rid,sv,f)][0]) else round(float(FI[(rid,sv,f)][0]),1) for f in FAIXAS] for sv in DIAS]
    pt=[[int(FI.get((rid,sv,f),(0,0))[1]) for f in FAIXAS] for sv in DIAS]
    hrs=[[int(H.get((rid,sv,h),0)) for h in range(24)] for sv in DIAS]
    fl=[]
    for sv in DIAS:
        gs=g[g.service_id==sv]
        fl.append([int(gs.s.min()),int(gs.s.max())] if len(gs) else None)
    f=lambda v: None if pd.isna(v) else (round(float(v),1))
    lines.append({'id':i,'r':rid,'n':r.linha,'nome':r.nome,'modo':r.modo,'op':r.operador,'tar':f(r.tarifa_rs),
        'cor':('#'+r.cor_linha) if isinstance(r.cor_linha,str) and len(r.cor_linha)==6 else None,
        'iv':iv,'pt':pt,'h':hrs,'fl':fl,
        'amp':[f(r.amplitude_servico_h_util),f(r.amplitude_servico_h_sabado),f(r.amplitude_servico_h_domingo)],
        'vel':f(r.velocidade_comercial_kmh),'ext':f(r.extensao_km),'p4':int(r.pop_400m_a_pe),'p8':int(r.pop_800m_a_pe),
        'circ':bool(r.circular),'g':geom,'bb':[int(allp[:,0].min()),int(allp[:,1].min()),int(allp[:,0].max()),int(allp[:,1].max())],
        'st':RS.get(rid,[]),'np':pontos_parada(st[['x','y']].values[RS.get(rid,[])].astype(float)),
        'tec':{'fr':None if pd.isna(r.frota_min_estimada_pico) else int(r.frota_min_estimada_pico),'vkm':None if pd.isna(r.veiculo_km_dia_util) else int(r.veiculo_km_dia_util),
               'tort':f(r.tortuosidade),'div':f(r.divergencia_ida_volta_pct),'ns':int(r.n_sentidos),'ppp':None if pd.isna(r.pop_por_partida_util) else int(r.pop_por_partida_util)}})
out={'faixas':FAIXAS,'dias':['Dia útil','Sábado','Domingo/feriado'],'linhas':lines,'paradas':[[int(a),int(b),n] for a,b,n in zip(st.x,st.y,st.stop_name)]}
json.dump(out,open(os.path.join(DST,'linhas.json'),'w'),separators=(',',':'),ensure_ascii=False)
print('linhas.json KB',os.path.getsize(os.path.join(DST,'linhas.json'))//1024,' pts',sum(len(gg)//2 for l in lines for gg in l['g']))
