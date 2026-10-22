import sys, os, numpy as np, pandas as pd
G_,APE,DST=sys.argv[1:4]
def r(n,**k): return pd.read_csv(os.path.join(G_,n+'.txt'),keep_default_na=False,**k)
ro=r('routes',dtype=str); ag=r('agency',dtype=str).set_index('agency_id').agency_name
fr=r('fare_rules',dtype=str).merge(r('fare_attributes',dtype=str)[['fare_id','price']])
B=ro[['route_id','route_short_name','route_long_name','agency_id','route_type','route_color']].copy()
B['operador']=B.agency_id.map(ag); B['modo']=B.route_type.map({'700':'Ônibus','702':'BRT','200':'Executivo'})
B['tarifa_rs']=B.route_id.map(fr.drop_duplicates('route_id').set_index('route_id').price).astype(float)
O=pd.read_csv(os.path.join(DST,'_oferta_dia.csv'),dtype={'route_id':str})
F=pd.read_csv(os.path.join(DST,'linhas_intervalo_por_faixa.csv'),dtype={'route_id':str})
T=pd.read_csv(os.path.join(DST,'_tracado.csv'),dtype={'route_id':str})
Pp=pd.read_csv(os.path.join(DST,'_pop_linha.csv'),dtype={'route_id':str})
U=O[O.service_id=='U_REG'].drop(columns='service_id').add_suffix('_util').rename(columns={'route_id_util':'route_id'})
for sv,suf in [('S_REG','sabado'),('D_REG','domingo')]:
    U=U.merge(O[O.service_id==sv][['route_id','partidas_dia','amplitude_servico_h']].rename(columns={'partidas_dia':f'partidas_dia_{suf}','amplitude_servico_h':f'amplitude_servico_h_{suf}'}),how='outer')
fx={'Pico manhã (6h–9h)':'pico_manha','Entrepico (9h–16h)':'entrepico','Pico tarde (16h–19h)':'pico_tarde','Noite (19h–24h)':'noite','Madrugada (0h–5h)':'madrugada'}
I=F[(F.service_id=='U_REG')&(F.faixa.isin(fx))].assign(c=lambda d:'intervalo_min_util_'+d.faixa.map(fx)).pivot(index='route_id',columns='c',values='intervalo_medio_min').reset_index()
I2=F[(F.faixa=='Dia todo')&(F.service_id!='U_REG')].assign(c=lambda d:'intervalo_min_dia_todo_'+d.service_id.map({'S_REG':'sabado','D_REG':'domingo'})).pivot(index='route_id',columns='c',values='intervalo_medio_min').reset_index()
X=B.merge(U,how='left').merge(I,how='left').merge(I2,how='left').merge(T,how='left').merge(Pp,how='left')
X['pop_por_partida_util']=(X.pop_400m_a_pe/X.partidas_dia_util).round(0)
cols=['route_id','route_short_name','route_long_name','operador','modo','tarifa_rs','route_color',
 'partidas_dia_util','partidas_dia_sabado','partidas_dia_domingo',
 'intervalo_min_util_madrugada','intervalo_min_util_pico_manha','intervalo_min_util_entrepico','intervalo_min_util_pico_tarde','intervalo_min_util_noite','intervalo_min_dia_todo_sabado','intervalo_min_dia_todo_domingo',
 'primeira_partida_util','ultima_partida_util','amplitude_servico_h_util','amplitude_servico_h_sabado','amplitude_servico_h_domingo',
 'veiculo_km_dia_util','frota_min_estimada_pico_util',
 'extensao_km','velocidade_comercial_kmh','tortuosidade','divergencia_ida_volta_pct','n_sentidos','circular',
 'pop_400m_a_pe','pop_800m_a_pe','pop_por_partida_util','pct_pop_30pct_renda_mais_baixa','pct_pop_30pct_renda_mais_alta','pct_pretos_pardos','renda_media_area_atendida']
X=X[cols].rename(columns={'route_short_name':'linha','route_long_name':'nome','route_color':'cor_linha','primeira_partida_util':'primeira_partida_util','frota_min_estimada_pico_util':'frota_min_estimada_pico'})
X.sort_values(['modo','linha']).to_csv(os.path.join(DST,'indicadores_linhas.csv'),index=False)
print(X.shape); print(X.isna().sum()[X.isna().sum()>0].to_dict())
