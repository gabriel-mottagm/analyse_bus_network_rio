import sys, os, numpy as np, pandas as pd
C,OS,OUT,OUTP=sys.argv[1:5]
r=np.load(os.path.join(OUTP,'pontos_resultado.npz')); dw,de,freq,nlin=r['dw'],r['de'],r['freq'],r['nlin']
ps=pd.read_csv(os.path.join(OS,'pontos_setores.csv.gz'))
S=pd.read_csv(os.path.join(OUT,'setores_cobertura.csv'))   # atributos + indicadores em linha reta (mesma ordem de setores)
ps['dw']=dw[ps.p.values]; ps['de']=de[ps.p.values]; ps['f']=freq[ps.p.values]
R=400
ps['cob']=np.where(ps.dw<=R,ps['pop'],0); ps['cob300']=np.where(ps.dw<=300,ps['pop'],0); ps['cob500']=np.where(ps.dw<=500,ps['pop'],0); ps['cob800']=np.where(ps.dw<=800,ps['pop'],0)
ps['cob_reta']=np.where(ps.de<=R,ps['pop'],0)
ps['f_eff']=np.where(ps.dw<=R,ps.f,0)
ps['bom']=np.where((ps.dw<=R)&(ps.f>=10),ps['pop'],0)
ps['wd']=np.minimum(ps.dw,5000)*ps['pop']; ps['wf']=ps.f_eff*ps['pop']
m=(ps.de>100)&np.isfinite(ps.dw); ps['wr']=np.where(m,ps.dw/ps.de,0)*ps['pop']; ps['wrp']=np.where(m,ps['pop'],0)
cls=np.select([ps.dw>R,ps.f<4,ps.f<10,ps.f<30],[0,1,2,3],4); ps['cls']=cls
A=ps.groupby('s')[['pop','cob','cob300','cob500','cob800','cob_reta','bom','wd','wf','wr','wrp']].sum()
S=S.join(A,how='left')
S['pct_pop_400m_a_pe']=(100*S.cob/S['pop']).round(1); S['dist_media_a_pe_m']=(S.wd/S['pop']).round(0)
S['onibus_h_pico_400m_a_pe']=(S.wf/S['pop']).round(1); S['fator_desvio']=(S.wr/S.wrp).round(2)
cols=['cd_setor','bairro','ra','ap','populacao','area_km2','renda_media_responsavel','branca','preta','parda','amarela','indigena','pct_pop_400m','pct_pop_400m_a_pe','dist_media_parada_m','dist_media_a_pe_m','onibus_h_pico_400m','onibus_h_pico_400m_a_pe','fator_desvio']
S.rename(columns={'pct_pop_400m':'pct_pop_400m_reta_uniforme','dist_media_parada_m':'dist_media_reta_uniforme_m','onibus_h_pico_400m':'onibus_h_pico_400m_reta_uniforme'})\
 [[c.replace('pct_pop_400m','pct_pop_400m_reta_uniforme') if c=='pct_pop_400m' else c.replace('dist_media_parada_m','dist_media_reta_uniforme_m') if c=='dist_media_parada_m' else c.replace('onibus_h_pico_400m','onibus_h_pico_400m_reta_uniforme') if c=='onibus_h_pico_400m' else c for c in cols]]\
 .to_csv(os.path.join(OUTP,'setores_cobertura_a_pe.csv'),index=False)
def agg(by):
    B=S.groupby(by)[['populacao','area_km2','cob300','cob','cob500','cob800','cob_reta','bom','wd','wf','wr','wrp']].sum()
    o=pd.DataFrame({'populacao':B.populacao,'densidade_hab_km2':(B.populacao/B.area_km2).round(0),
      'pct_300m_a_pe':(100*B.cob300/B.populacao).round(1),'pct_400m_a_pe':(100*B.cob/B.populacao).round(1),'pct_500m_a_pe':(100*B.cob500/B.populacao).round(1),'pct_800m_a_pe':(100*B.cob800/B.populacao).round(1),
      'pct_400m_linha_reta':(100*B.cob_reta/B.populacao).round(1),'pct_400m_a_pe_10onibus_h':(100*B.bom/B.populacao).round(1),
      'dist_media_a_pe_m':(B.wd/B.populacao).round(0),'onibus_h_pico_medio':(B.wf/B.populacao).round(1),'fator_desvio_medio':(B.wr/B.wrp).round(2)})
    return o.reset_index()
agg(['ap','ra','bairro']).to_csv(os.path.join(OUTP,'bairros_cobertura_a_pe.csv'),index=False)
agg(['ap','ra']).to_csv(os.path.join(OUTP,'ra_cobertura_a_pe.csv'),index=False)
Ap=agg(['ap']); Ap.to_csv(os.path.join(OUTP,'ap_cobertura_a_pe.csv'),index=False); print(Ap.to_string(index=False))
# níveis de serviço
tot=ps['pop'].sum(); lv=ps.groupby('cls')['pop'].sum()/tot*100
lab=['Sem parada a até 400 m a pé','Menos de 4 ônibus/h','4 a 10 ônibus/h','10 a 30 ônibus/h','30 ou mais ônibus/h']
NV=pd.DataFrame({'nivel':lab,'pct_pop':lv.reindex(range(5)).fillna(0).round(1).values}); print(NV.to_string(index=False)); NV.to_csv(os.path.join(OUTP,'nivel_servico_a_pe.csv'),index=False)
# equidade por renda (mesmos decis da análise anterior)
Sp=S[(S.populacao>0)&(S.renda_media_responsavel>0)].sort_values('renda_media_responsavel')
Sp['decil_renda']=np.minimum((Sp.populacao.cumsum()/Sp.populacao.sum()*10).astype(int)+1,10)
E=Sp.groupby('decil_renda').agg(populacao=('populacao','sum'),renda_med=('renda_media_responsavel','median'),cob=('cob','sum'),cob_reta=('cob_reta','sum'),bom=('bom','sum'),wf=('wf','sum'),wd=('wd','sum'),wr=('wr','sum'),wrp=('wrp','sum'))
E['pct_400m_a_pe']=(100*E.cob/E.populacao).round(1); E['pct_400m_linha_reta']=(100*E.cob_reta/E.populacao).round(1)
E['pct_400m_a_pe_10onibus_h']=(100*E.bom/E.populacao).round(1); E['onibus_h_pico_medio']=(E.wf/E.populacao).round(1); E['dist_media_a_pe_m']=(E.wd/E.populacao).round(0); E['fator_desvio']=(E.wr/E.wrp).round(2)
E=E[['populacao','renda_med','pct_400m_a_pe','pct_400m_linha_reta','pct_400m_a_pe_10onibus_h','onibus_h_pico_medio','dist_media_a_pe_m','fator_desvio']]
print(E.to_string()); E.reset_index().to_csv(os.path.join(OUTP,'equidade_renda_a_pe.csv'),index=False)
rows=[]
for c in ['branca','preta','parda']:
    w=S[c].fillna(0); sh=lambda col:(S[col]/S['pop'].replace(0,np.nan)).fillna(0)
    rows.append({'cor_raca':c,'populacao':int(w.sum()),'pct_400m_a_pe':round(100*(w*sh('cob')).sum()/w.sum(),1),'pct_400m_a_pe_10onibus_h':round(100*(w*sh('bom')).sum()/w.sum(),1),
                 'dist_media_a_pe_m':round((w*(S.wd/S['pop']).fillna(0)).sum()/w.sum(),0)})
E2=pd.DataFrame(rows); print(E2.to_string(index=False)); E2.to_csv(os.path.join(OUTP,'equidade_cor_raca_a_pe.csv'),index=False)
# prioridade: 30% de renda mais baixa e (sem parada a 400 m a pé ou <10 ônibus/h)
dec=pd.Series(-1,index=S.index); dec[Sp.index]=Sp.decil_renda
ps['dec']=dec.reindex(ps.s.values).values
pri=(ps.dec>=1)&(ps.dec<=3)&((ps.dw>R)|(ps.f<10))
ps['pri']=np.where(pri,ps['pop'],0); ps['pri_sem']=np.where(pri&(ps.dw>R),ps['pop'],0)
PB=ps.groupby(S.bairro.values[ps.s.values])[['pri','pri_sem']].sum().rename(columns={'pri':'pop_prioritaria','pri_sem':'dos_quais_sem_parada_400m_a_pe'}).round(0).astype(int)
PB['pop_bairro']=S.groupby('bairro').populacao.sum().reindex(PB.index); PB['pct_bairro']=(100*PB.pop_prioritaria/PB.pop_bairro).round(1)
PB=PB.sort_values('pop_prioritaria',ascending=False); PB.rename_axis('bairro').reset_index().to_csv(os.path.join(OUTP,'prioridade_bairros_a_pe.csv'),index=False)
low=ps[(ps.dec>=1)&(ps.dec<=3)]['pop'].sum(); hi=ps[ps.dec>=8]
print(f"pop prioritária: {ps.pri.sum():,.0f} = {100*ps.pri.sum()/low:.0f}% dos 30% de renda mais baixa; entre os 30% de renda mais alta: {100*hi[(hi.dw>R)|(hi.f<10)]['pop'].sum()/hi['pop'].sum():.0f}%")
print(PB.head(12).to_string())
# células para os mapas: salva por ponto a classe e o decil dominante
ps[['p','s','pop','dec','cls']].to_csv(os.path.join(OUTP,'pontos_mapa.csv.gz'),index=False)
