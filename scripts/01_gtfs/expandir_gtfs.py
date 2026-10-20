import pandas as pd, numpy as np, sys, os
D,O=sys.argv[1],sys.argv[2]
def r(n,**k): return pd.read_csv(os.path.join(D,n+'.txt'),keep_default_na=False,**k)
def secs(t):
    p=t.str.split(':',expand=True).astype(int); return p[0]*3600+p[1]*60+p[2]
def hms(s): s=np.asarray(s,dtype=int); return pd.Series([f"{a:02d}:{b:02d}:{c:02d}" for a,b,c in zip(s//3600,(s%3600)//60,s%60)])
ag=r('agency',dtype=str); ro=r('routes',dtype=str); tr=r('trips',dtype=str); st=r('stops',dtype=str)
stt=r('stop_times',dtype={'trip_id':str,'stop_id':str}); fr=r('frequencies',dtype={'trip_id':str})
stt['a']=secs(stt.arrival_time); stt=stt.sort_values(['trip_id','stop_sequence'])
g=stt.groupby('trip_id')
tm=g.agg(t0=('a','first'),t1=('a','last'),o=('stop_id','first'),d=('stop_id','last'),n=('stop_id','size'),dist=('shape_dist_traveled','last'))
stt['off']=stt.a-stt.trip_id.map(tm.t0)
# 1) expand frequencies
fr['s']=secs(fr.start_time); fr['e']=secs(fr.end_time); fr['h']=fr.headway_secs.astype(int)
fr['k']=np.ceil((fr.e-fr.s)/fr.h).astype(int)
rep=fr.loc[fr.index.repeat(fr.k)].copy()
rep['i']=rep.groupby(level=0).cumcount()
rep['dep']=rep.s+rep.i*rep.h
P=rep[['trip_id','dep','h']].rename(columns={'h':'headway_s'})
P['origem_horario']='frequencia'
fx=tr[~tr.trip_id.isin(fr.trip_id)][['trip_id']].copy(); fx['dep']=fx.trip_id.map(tm.t0); fx['headway_s']=np.nan; fx['origem_horario']='fixo'
P=pd.concat([P,fx],ignore_index=True)
# enrich
tipo={'700':'Ônibus','702':'BRT','200':'Executivo'}; dia={'U_REG':'Dia útil','S_REG':'Sábado','D_REG':'Domingo/feriado'}
R=ro.merge(ag[['agency_id','agency_name']],how='left').set_index('route_id')
T=tr.set_index('trip_id')
P=P.join(T[['route_id','service_id','direction_id','trip_headsign','shape_id']],on='trip_id')
P['linha']=P.route_id.map(R.route_short_name); P['nome_linha']=P.route_id.map(R.route_long_name)
P['operador']=P.route_id.map(R.agency_name); P['modo']=P.route_id.map(R.route_type).map(tipo)
P['tipo_dia']=P.service_id.map(dia)
dur=(P.trip_id.map(tm.t1)-P.trip_id.map(tm.t0))
P['hora_partida']=hms(P.dep).values; P['hora_chegada']=hms(P.dep+dur).values
P['hora_do_dia']=(P.dep//3600)%24
P['duracao_min']=(dur/60).round(1); P['extensao_km']=(P.trip_id.map(tm.dist)/1000).round(2)
P['velocidade_kmh']=(P.extensao_km/(P.duracao_min/60)).round(1)
P['n_paradas']=P.trip_id.map(tm.n)
SN=st.set_index('stop_id').stop_name
P['parada_origem']=P.trip_id.map(tm.o).map(SN); P['parada_destino']=P.trip_id.map(tm.d).map(SN)
P['headway_min']=(P.headway_s/60).round(1)
h=P.hora_do_dia
P['periodo']=np.select([h.between(0,3),h.between(4,5),h.between(6,8),h.between(9,15),h.between(16,19)],['Madrugada','Início','Pico manhã','Entrepico','Pico tarde'],'Noite')
P=P.sort_values(['service_id','route_id','direction_id','dep']).reset_index(drop=True)
P.insert(0,'partida_id',np.arange(1,len(P)+1))
cols=['partida_id','tipo_dia','service_id','operador','modo','route_id','linha','nome_linha','direction_id','trip_headsign','trip_id','shape_id','hora_partida','hora_chegada','hora_do_dia','periodo','headway_min','duracao_min','extensao_km','velocidade_kmh','n_paradas','parada_origem','parada_destino','origem_horario']
P[cols].to_csv(os.path.join(O,'partidas_expandidas.csv'),index=False)
print("partidas:",len(P)); print(P.groupby('tipo_dia').size())
# 2) passagens por parada (expansão completa, agregada)
J=P[['trip_id','dep','service_id','route_id']].merge(stt[['trip_id','stop_id','off']],on='trip_id')
J['t']=J.dep+J.off; J['hora']=(J.t//3600)%24
print("passagens totais (linhas na expansão completa):",len(J))
A=J.groupby(['stop_id','service_id','hora']).agg(passagens=('t','size'),linhas=('route_id','nunique')).reset_index()
A['tipo_dia']=A.service_id.map(dia); A['nome_parada']=A.stop_id.map(SN)
A.to_csv(os.path.join(O,'passagens_parada_hora.csv'),index=False)
S=J.groupby(['stop_id','service_id']).agg(passagens=('t','size'),linhas=('route_id','nunique')).unstack('service_id',fill_value=0)
S.columns=[f"{a}_{b}" for a,b in S.columns]
S=S.join(st.set_index('stop_id')[['stop_name','stop_lat','stop_lon']])
pk=J[(J.service_id=='U_REG')&(J.t>=6*3600)&(J.t<9*3600)].groupby('stop_id').size()
S['passagens_pico_manha_util']=pk.reindex(S.index).fillna(0).astype(int)
S['intervalo_medio_pico_min']=(180/S.passagens_pico_manha_util.replace(0,np.nan)).round(1)
S.reset_index().to_csv(os.path.join(O,'resumo_paradas.csv'),index=False)
print(S.sort_values('passagens_U_REG',ascending=False).head(5)[['stop_name','passagens_U_REG','linhas_U_REG']])
