import pandas as pd, numpy as np, sys, os
D=sys.argv[1]; O=sys.argv[2]
def r(n,**k): return pd.read_csv(os.path.join(D,n+'.txt'),keep_default_na=False,**k)
ro=r('routes',dtype=str); tr=r('trips',dtype=str); fru=r('fare_rules',dtype=str); st=r('stops',dtype=str)
stt=r('stop_times',dtype={'trip_id':str,'stop_id':str}); fr=r('frequencies',dtype={'trip_id':str})
x=pd.read_csv(os.path.join(O,'freq_trips.csv'),dtype={'trip_id':str,'route_id':str,'direction_id':str})
print("rotas sem tarifa:", ro[~ro.route_id.isin(fru.route_id)][['route_short_name','route_long_name','agency_id','route_type']].values.tolist())
nf=tr[~tr.trip_id.isin(fr.trip_id)]
first=stt[stt.stop_sequence==0].set_index('trip_id').arrival_time
print("trips sem freq: rotas", nf.route_id.nunique(), nf.merge(ro,on='route_id').route_short_name.value_counts().head(8).to_dict(), " horários ex:", first.reindex(nf.trip_id).head(5).tolist())
# departures by hour (expand)
rows=[]
for s,e,h,sv,rid in x[['s','e','h','service_id','route_id']].itertuples(index=False):
    for t in range(int(s),int(e),int(h)): rows.append((sv,rid,(t//3600)))
dep=pd.DataFrame(rows,columns=['service','route_id','hour'])
nfx=nf.copy(); nfx['hour']=first.reindex(nf.trip_id).str[:2].astype(int).values
dep=pd.concat([dep,nfx.rename(columns={'service_id':'service'})[['service','route_id','hour']]])
print("partidas totais por dia-tipo:", dep.groupby('service').size().to_dict())
h=dep.groupby(['hour','service']).size().unstack(fill_value=0); print(h.to_string())
h.to_csv(os.path.join(O,'dep_by_hour.csv'))
top=dep[dep.service=='U_REG'].groupby('route_id').size().sort_values(ascending=False)
print("top rotas dia útil:", [(ro.set_index('route_id').loc[i,'route_short_name'],ro.set_index('route_id').loc[i,'route_long_name'],int(v)) for i,v in top.head(8).items()])
print("rotas com <=5 partidas em dia útil:", (top<=5).sum(), " sem serviço útil:", (~ro.route_id.isin(top.index)).sum())
# headway in pico 6-9 weekday
pk=x[(x.service_id=='U_REG')&(x.s<9*3600)&(x.e>6*3600)]
print("headway pico manhã por rota (min, menor janela) desc:", (pk.groupby(['route_id','direction_id']).h.min()/60).describe().round(1).to_dict())
# stops: routes per stop
sr=stt.merge(tr[['trip_id','route_id']]).groupby('stop_id').route_id.nunique().sort_values(ascending=False)
sn=st.set_index('stop_id').stop_name
print("paradas com mais linhas:", [(sn[i],int(v)) for i,v in sr.head(8).items()])
print("linhas por parada desc:", sr.describe().round(1).to_dict(), " paradas com 1 linha:", (sr==1).sum())
# directions
d=tr.groupby('route_id').direction_id.nunique(); print("rotas só com 1 sentido:", (d==1).sum())
print("headsign Circular rotas:", tr[tr.trip_headsign=='Circular'].route_id.nunique())
# weekday holidays U_REG; feed dates
