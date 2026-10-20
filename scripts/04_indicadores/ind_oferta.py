# Indicadores de oferta por linha × tipo de dia (e intervalo por faixa horária, método busmadrid)
import sys, os, numpy as np, pandas as pd
OUT,DST=sys.argv[1],sys.argv[2]
P=pd.read_csv(os.path.join(OUT,'partidas_expandidas.csv'),dtype={'route_id':str})
P['dep_s']=P.hora_partida.str.split(':',expand=True).astype(int).pipe(lambda d:d[0]*3600+d[1]*60+d[2])
P['h']=P.hora_do_dia
FAIXAS={'Madrugada (0h–5h)':range(0,5),'Início (5h–6h)':range(5,6),'Pico manhã (6h–9h)':range(6,9),'Entrepico (9h–16h)':range(9,16),'Pico tarde (16h–19h)':range(16,19),'Noite (19h–24h)':range(19,24),'Dia todo':range(0,24)}
rows=[]
for (rid,sv),g in P.groupby(['route_id','service_id']):
    for fx,hrs in FAIXAS.items():
        ints=[];parts=0
        for d,gd in g.groupby('direction_id'):
            x=gd[gd.h.isin(hrs)]
            if len(x)==0: continue
            H=x.h.nunique(); E=len(x); ints.append(60*H/E); parts+=E
        rows.append({'route_id':rid,'service_id':sv,'faixa':fx,'partidas':parts,'intervalo_medio_min':round(np.mean(ints),1) if ints else np.nan})
F=pd.DataFrame(rows); F['tipo_dia']=F.service_id.map({'U_REG':'Dia útil','S_REG':'Sábado','D_REG':'Domingo/feriado'})
F.to_csv(os.path.join(DST,'linhas_intervalo_por_faixa.csv'),index=False)
# por linha × dia: partidas, amplitude, primeira/última, veículo-km, frota mínima no pico
rows=[]
for (rid,sv),g in P.groupby(['route_id','service_id']):
    amp=[];first=[];last=[];fleet=0.0
    for d,gd in g.groupby('direction_id'):
        amp.append((gd.dep_s.max()-gd.dep_s.min())/3600); first.append(gd.dep_s.min()); last.append(gd.dep_s.max())
        pk=gd[gd.h.isin(range(6,9))]
        if len(pk): fleet+=len(pk)/3.0*(pk.duracao_min.mean()/60)   # ônibus/h × duração da viagem (h)
    hms=lambda s:f"{int(s//3600):02d}:{int(s%3600//60):02d}"
    rows.append({'route_id':rid,'service_id':sv,'partidas_dia':len(g),'amplitude_servico_h':round(np.mean(amp),1),
                 'primeira_partida':hms(min(first)),'ultima_partida':hms(max(last)),
                 'veiculo_km_dia':round((g.extensao_km).sum(),0),'frota_min_estimada_pico':int(np.ceil(fleet)) if fleet>0 else 0})
D=pd.DataFrame(rows); D.to_csv(os.path.join(DST,'_oferta_dia.csv'),index=False)
print(F[(F.service_id=='U_REG')&(F.faixa=='Pico manhã (6h–9h)')].intervalo_medio_min.describe().round(1).to_dict())
print(D[D.service_id=='U_REG'][['partidas_dia','amplitude_servico_h','veiculo_km_dia','frota_min_estimada_pico']].describe().round(1).T)
print('frota total estimada (dia útil, pico):',D[D.service_id=='U_REG'].frota_min_estimada_pico.sum())
