import numpy as np, pandas as pd, sys, os
from scipy.spatial import cKDTree
G, C, O = sys.argv[1], sys.argv[2], sys.argv[3]   # gtfs dir, censo dir, saída
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']; nx=int(nx)
ci,co,cp=z['cell_idx'],z['cell_own'],z['cell_pop']
keep=cp>0; ci,co,cp=ci[keep],co[keep],cp[keep]
cx=x0+(ci%nx+0.5)*CELL; cy=y0+(ci//nx+0.5)*CELL
S=pd.read_csv(os.path.join(C,'setores_atributos.csv'))
TOT=cp.sum(); print("células com população:",len(cp)," pop:",round(TOT))
def r(n,**k): return pd.read_csv(os.path.join(G,n+'.txt'),keep_default_na=False,**k)
st=r('stops',dtype=str); ro=r('routes',dtype=str); tr=r('trips',dtype=str)
stt=r('stop_times',dtype={'trip_id':str,'stop_id':str},usecols=['trip_id','stop_id'])
st=st[st.location_type!='1'].copy()
st['x']=(st.stop_lon.astype(float)-LON0)*KX; st['y']=(st.stop_lat.astype(float)-LAT0)*KY
st=st.set_index('stop_id')
# 1) distância à parada mais próxima (todas e só BRT)
T=cKDTree(st[['x','y']].values); d,_=T.query(np.column_stack([cx,cy]))
brt_routes=set(ro.route_id[ro.route_type=='702'])
rs=stt.merge(tr[['trip_id','route_id','direction_id']]).drop_duplicates(['stop_id','route_id','direction_id'])
brt_stops=rs[rs.route_id.isin(brt_routes)].stop_id.unique()
db,_=cKDTree(st.loc[brt_stops,['x','y']].values).query(np.column_stack([cx,cy]))
rede=[]
for R in [200,300,400,500,800,1000]:
    rede.append({'raio_m':R,'pop_coberta':round(cp[d<=R].sum()),'pct':round(100*cp[d<=R].sum()/TOT,1),
                 'pop_coberta_brt':round(cp[db<=R].sum()),'pct_brt':round(100*cp[db<=R].sum()/TOT,1)})
rede=pd.DataFrame(rede); print(rede.to_string(index=False)); rede.to_csv(os.path.join(O,'cobertura_rede.csv'),index=False)
# 2) ônibus/hora no pico (dia útil, partidas 6h-9h na origem) por linha-sentido
P=pd.read_csv(os.path.join(sys.argv[4],'partidas_expandidas.csv'),usecols=['service_id','route_id','direction_id','hora_partida'],dtype={'route_id':str})
hh=P.hora_partida.str[:2].astype(int)
pk=P[(P.service_id=='U_REG')&(hh>=6)&(hh<9)].groupby(['route_id','direction_id']).size()/3.0
dia=P[P.service_id=='U_REG'].groupby('route_id').size()
CT=cKDTree(np.column_stack([cx,cy]))
R=400
freq=np.zeros(len(cp)); nlin=np.zeros(len(cp),dtype=np.int32)
linhas=[]
for rid,grp in rs.groupby('route_id'):
    best={}
    for dirc,g2 in grp.groupby('direction_id'):
        pts=st.loc[g2.stop_id,['x','y']].values
        idx=np.unique(np.concatenate([np.asarray(a,dtype=np.int64) for a in CT.query_ball_point(pts,R)]+[np.array([],dtype=np.int64)]))
        f=pk.get((rid,int(dirc)),0.0)
        for c in idx.tolist():
            if best.get(c,-1)<f: best[c]=f
    idx=np.fromiter(best.keys(),dtype=np.int64); fv=np.fromiter(best.values(),dtype=float)
    freq[idx]+=fv; nlin[idx]+=1
    linhas.append({'route_id':rid,'pop_400m':round(cp[idx].sum()),'n_paradas':grp.stop_id.nunique(),'partidas_dia_util':int(dia.get(rid,0)),'onibus_h_pico_ambos_sentidos':round(pk.get((rid,0),0)+pk.get((rid,1),0),1)})
L=pd.DataFrame(linhas).merge(ro[['route_id','agency_id','route_short_name','route_long_name','route_type']])
ag=r('agency',dtype=str).set_index('agency_id').agency_name; L['operador']=L.agency_id.map(ag)
L['modo']=L.route_type.map({'700':'Ônibus','702':'BRT','200':'Executivo'})
L['pct_pop_cidade']=(100*L.pop_400m/TOT).round(2)
L=L[['route_id','route_short_name','route_long_name','operador','modo','n_paradas','partidas_dia_util','onibus_h_pico_ambos_sentidos','pop_400m','pct_pop_cidade']].sort_values('pop_400m',ascending=False)
L.to_csv(os.path.join(O,'linhas_populacao.csv'),index=False); print(L.head(5).to_string(index=False)); print(L.pop_400m.describe().round(0).to_dict())
# 3) por parada
B=CT.query_ball_point(st[['x','y']].values,R)
st['pop_400m']=[round(cp[np.asarray(b,dtype=np.int64)].sum()) if len(b) else 0 for b in B]
rp=pd.read_csv(os.path.join(sys.argv[4],'resumo_paradas.csv'),dtype={'stop_id':str}).set_index('stop_id')
PS=rp.join(st[['pop_400m']]); PS.reset_index().to_csv(os.path.join(O,'paradas_populacao.csv'),index=False)
# 4) classes de nível de serviço por célula
cls=np.select([d>R, freq<4, freq<10, freq<30],['0 Sem parada a 400 m','1 Menos de 4 ônibus/h','2 4 a 10 ônibus/h','3 10 a 30 ônibus/h'],'4 30+ ônibus/h')
np.savez_compressed(os.path.join(O,'celulas.npz'),ci=ci,cp=cp,d=d,db=db,freq=freq,nlin=nlin,co=co)
cel=pd.DataFrame({'own':co,'pop':cp,'d':d,'freq':freq,'nlin':nlin,'cls':cls})
print(cel.groupby('cls')['pop'].sum().div(TOT).mul(100).round(1))
# 5) por setor (média ponderada pela população)
cel['wd']=cel.d*cel['pop']; cel['wf']=cel.freq*cel['pop']; cel['wl']=cel.nlin*cel['pop']; cel['cob']=np.where(cel.d<=R,cel['pop'],0)
for k,R2 in [('cov300',300),('cov500',500),('cov800',800)]: cel[k]=np.where(cel.d<=R2,cel['pop'],0)
cel['bom']=np.where((cel.d<=R)&(cel.freq>=10),cel['pop'],0)
a=cel.groupby('own')[['pop','wd','wf','wl','cob','cov300','cov500','cov800','bom']].sum()
S=S.join(a,how='left').fillna({'pop':0})
S['dist_media_parada_m']=(S.wd/S['pop']).round(0); S['onibus_h_pico_400m']=(S.wf/S['pop']).round(1); S['linhas_400m']=(S.wl/S['pop']).round(1)
S['pct_pop_400m']=(100*S['cob']/S['pop']).round(1)
S.rename(columns={'total_de_p':'populacao','valor_do_r':'renda_media_responsavel','cor_ou_rau':'branca','cor_ou_r_1':'preta','cor_ou_r_2':'amarela','cor_ou_r_3':'parda','cor_ou_r_4':'indigena'},inplace=True)
cols=['cd_setor','bairro','ra','ap','populacao','area_km2','renda_media_responsavel','branca','preta','parda','amarela','indigena','dist_media_parada_m','pct_pop_400m','onibus_h_pico_400m','linhas_400m']
S[cols].to_csv(os.path.join(O,'setores_cobertura.csv'),index=False)
# 6) agregações territoriais
def agg(by):
    A=S.groupby(by)[['populacao','area_km2','cov300','cob','cov500','cov800','bom','wd','wf']].sum()
    out=pd.DataFrame({'populacao':A.populacao,'densidade_hab_km2':(A.populacao/A.area_km2).round(0),
        'pct_300m':(100*A.cov300/A.populacao).round(1),'pct_400m':(100*A.cob/A.populacao).round(1),'pct_500m':(100*A.cov500/A.populacao).round(1),'pct_800m':(100*A.cov800/A.populacao).round(1),
        'pct_400m_10onibus_h':(100*A.bom/A.populacao).round(1),'dist_media_parada_m':(A.wd/A.populacao).round(0),'onibus_h_pico_medio':(A.wf/A.populacao).round(1)})
    return out.reset_index()
agg(['ap','ra','bairro']).to_csv(os.path.join(O,'bairros_cobertura.csv'),index=False)
A=agg(['ap']); print(A.to_string(index=False)); A.to_csv(os.path.join(O,'ap_cobertura.csv'),index=False)
agg(['ap','ra']).to_csv(os.path.join(O,'ra_cobertura.csv'),index=False)
# 7) equidade: renda (decis de população) e cor/raça
Sp=S[S.populacao>0].sort_values('renda_media_responsavel')
Sp['decil_renda']=np.minimum((Sp.populacao.cumsum()/Sp.populacao.sum()*10).astype(int)+1,10)
E=Sp.groupby('decil_renda').agg(populacao=('populacao','sum'),renda_med=('renda_media_responsavel','median'),cob=('cob','sum'),bom=('bom','sum'),wf=('wf','sum'),wd=('wd','sum'))
E['pct_400m']=(100*E['cob']/E.populacao).round(1); E['pct_400m_10onibus_h']=(100*E.bom/E.populacao).round(1); E['onibus_h_pico_medio']=(E.wf/E.populacao).round(1); E['dist_media_parada_m']=(E.wd/E.populacao).round(0)
E=E[['populacao','renda_med','pct_400m','pct_400m_10onibus_h','onibus_h_pico_medio','dist_media_parada_m']]; print(E.to_string()); E.reset_index().to_csv(os.path.join(O,'equidade_renda.csv'),index=False)
rows=[]
for c in ['branca','preta','parda','amarela','indigena']:
    w=S[c].fillna(0); share_cov=(S['cob']/S['pop'].replace(0,np.nan)).fillna(0); share_bom=(S.bom/S['pop'].replace(0,np.nan)).fillna(0)
    rows.append({'cor_raca':c,'populacao':int(w.sum()),'pct_400m':round(100*(w*share_cov).sum()/w.sum(),1),'pct_400m_10onibus_h':round(100*(w*share_bom).sum()/w.sum(),1),'onibus_h_pico_medio':round((w*S.onibus_h_pico_400m.fillna(0)).sum()/w.sum(),1)})
E2=pd.DataFrame(rows); print(E2.to_string(index=False)); E2.to_csv(os.path.join(O,'equidade_cor_raca.csv'),index=False)
