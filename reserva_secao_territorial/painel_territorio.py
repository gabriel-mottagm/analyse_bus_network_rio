# Camadas territoriais (grade de 100 m codificada em PNG) e dados de bairros para o painel
import sys, os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
C,OS,APE,DST=sys.argv[1:5]; AG=100.0
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']; nx,ny=int(nx),int(ny)
p=np.load(os.path.join(OS,'pontos.npz')); px,py=p['x'],p['y']
r=np.load(os.path.join(APE,'pontos_resultado.npz')); dw,de,freq=r['dw'],r['de'],r['freq']
M=pd.read_csv(os.path.join(APE,'pontos_mapa.csv.gz'))
S=pd.read_csv(os.path.join(C,'setores_atributos.csv'))
gx0=np.floor(x0/AG)*AG; gy0=np.floor(y0/AG)*AG
GX=int(np.ceil((x0+nx*CELL-gx0)/AG))+1; GY=int(np.ceil((y0+ny*CELL-gy0)/AG))+1
mx,my=px[M.p.values],py[M.p.values]
k=(np.clip(((my-gy0)//AG).astype(int),0,GY-1))*GX+np.clip(((mx-gx0)//AG).astype(int),0,GX-1)
pop=M['pop'].values; cls=M.cls.values; dec=M.dec.values
def dominant(lbl,n):
    acc=np.zeros((n,GX*GY))
    for c in range(n):
        m=lbl==c; np.add.at(acc[c],k[m],pop[m])
    out=acc.argmax(0)+1; out[acc.sum(0)==0]=0; return out
ptot=np.bincount(k,weights=pop,minlength=GX*GY); dens=ptot/((AG/1000)**2)
L1=dominant(cls,5)                                   # 1..5 nível de serviço
serv=np.select([cls<=2,cls==3],[0,1],2); t=np.where(dec>0,np.select([dec<=3,dec<=7],[0,1],2),-1)
L2=dominant(np.where(t>=0,(2-serv)*3+(2-t),-1),9)     # 1..9 renda × oferta
pri=(dec>=1)&(dec<=3)&(serv==0)
pd_=np.bincount(k[pri],weights=pop[pri],minlength=GX*GY)/((AG/1000)**2)
L3=np.select([pd_<=0,pd_<2000,pd_<5000,pd_<10000],[0,1,2,3],4)
ddw=dw[M.p.values]; dde=de[M.p.values]; ok=(dde>100)&np.isfinite(ddw)&(ddw<5000)
rat=np.where(ok,ddw/np.maximum(dde,1),0)
wr=np.bincount(k[ok],weights=(rat*pop)[ok],minlength=GX*GY); wp=np.bincount(k[ok],weights=pop[ok],minlength=GX*GY)
fd=np.where(wp>0,wr/np.maximum(wp,1e-9),0)
L4=np.select([wp>0,ptot>0],[np.select([fd<1.3,fd<1.6,fd<2.0],[1,2,3],4),5],0)   # 5 = parada a menos de 100 m
DN=np.select([ptot<=0,dens<1000,dens<3000,dens<6000,dens<10000,dens<20000],[0,1,2,3,4,5],6)
def img(a,b,c,name):
    arr=np.stack([a,b,c],1).reshape(GY,GX,3)[::-1].astype(np.uint8)   # linha 0 = norte
    plt.imsave(os.path.join(DST,name),arr)
# bairro de cada quadrícula de 100 m (moda das células de 20 m do território)
S0=pd.read_csv(os.path.join(C,'setores_atributos.csv')); bcodes,bnames=pd.factorize(S0.bairro)
ci=z['cell_idx']; cx20=x0+(ci%nx+0.5)*CELL; cy20=y0+(ci//nx+0.5)*CELL
k20=(np.clip(((cy20-gy0)//AG).astype(int),0,GY-1))*GX+np.clip(((cx20-gx0)//AG).astype(int),0,GX-1)
acc=pd.DataFrame({'k':k20,'b':bcodes[z['cell_own']]}).groupby(['k','b']).size().reset_index().sort_values(0).drop_duplicates('k',keep='last')
BX=np.zeros(GX*GY,dtype=int); BX[acc.k.values]=acc.b.values+1
img(L1*40,L2*25,L3*50,'camadas_a.png'); img(L4*40,DN*35,BX,'camadas_b.png')
print('grade',GX,GY,' células com moradores',(ptot>0).sum())
# ---------- bairros ----------
B=pd.read_csv(os.path.join(APE,'bairros_cobertura_a_pe.csv'))
PB=pd.read_csv(os.path.join(APE,'prioridade_bairros_a_pe.csv')).set_index('bairro')
bai=S.bairro.values[M.s.values]
NV=pd.DataFrame({'b':bai,'c':cls,'p':pop}).groupby(['b','c']).p.sum().unstack(fill_value=0)
NV=NV.div(NV.sum(1),axis=0)
Sr=S[S.valor_do_r>0]; renda=(Sr.valor_do_r*Sr.total_de_p).groupby(Sr.bairro).sum()/Sr.total_de_p.groupby(Sr.bairro).sum()
# contornos por bairro (grade de 60 m, como no fundo do mapa)
def rdp(a,eps):
    if len(a)<3: return a
    st=[(0,len(a)-1)]; keep=np.zeros(len(a),bool); keep[0]=keep[-1]=True
    while st:
        i,j=st.pop(); pp,q=a[i],a[j]; seg=a[i+1:j]
        if len(seg)==0: continue
        d=q-pp; n=np.hypot(*d); v=seg-pp
        dist=np.abs(d[0]*v[:,1]-d[1]*v[:,0])/n if n>0 else np.hypot(v[:,0],v[:,1])
        kk=np.argmax(dist)
        if dist[kk]>eps: keep[i+1+kk]=True; st+=[(i,i+1+kk),(i+1+kk,j)]
    return a[keep]
F=3; own=np.full(nx*ny,-1,dtype=np.int32); own[z['cell_idx']]=z['cell_own']; own2=own.reshape(ny,nx)
NYb,NXb=ny//F,nx//F; o3=own2[:NYb*F,:NXb*F].reshape(NYb,F,NXb,F).transpose(0,2,1,3).reshape(NYb,NXb,F*F)
codes,names=pd.factorize(S.bairro); lab=np.where(o3>=0,codes[np.maximum(o3,0)],-1)
def mode(v):
    v=v[v>=0]; return np.bincount(v).argmax() if len(v) else -1
BL=np.apply_along_axis(mode,2,lab)
cgx=x0+(np.arange(NXb)+0.5)*CELL*F; cgy=y0+(np.arange(NYb)+0.5)*CELL*F
# paradas → bairro
L=json.load(open(os.path.join(DST,'linhas.json')))
stx=np.array([s[0] for s in L['paradas']]); sty=np.array([s[1] for s in L['paradas']])
def owner_at(x,y):
    cx=int((x-x0)//CELL); cy=int((y-y0)//CELL)
    for rr in range(0,6):
        best=None
        for dx in range(-rr,rr+1):
            for dy in range(-rr,rr+1):
                xx,yy=cx+dx,cy+dy
                if 0<=xx<nx and 0<=yy<ny and own2[yy,xx]>=0: return own2[yy,xx]
    return -1
st_b=np.array([S.bairro.values[o] if o>=0 else None for o in (owner_at(a,b) for a,b in zip(stx,sty))],dtype=object)
linhas_b={}
for l in L['linhas']:
    for b in set(st_b[l['st']]) - {None}: linhas_b.setdefault(b,[]).append(l['id'])
part=lambda i: L['linhas'][i]['pt'][0][5]
out=[]
B=B.set_index('bairro').reindex(list(bnames)).reset_index()
for _,row in B.iterrows():
    b=row.bairro; ci=list(names).index(b) if b in list(names) else None
    segs=[]; bb=None
    if ci is not None:
        fig=plt.figure(); cs=plt.contour(cgx,cgy,(BL==ci).astype(float),levels=[0.5]); plt.close(fig)
        for s in cs.allsegs[0]:
            if len(s)>=4: segs.append(np.round(rdp(np.asarray(s),25)).astype(int).ravel().tolist())
        if segs:
            a=np.vstack([np.array(s).reshape(-1,2) for s in segs]); bb=[int(a[:,0].min()),int(a[:,1].min()),int(a[:,0].max()),int(a[:,1].max())]
    nv=[round(float(NV.loc[b,c]*100),1) if b in NV.index and c in NV.columns else 0.0 for c in range(5)]
    pr=PB.loc[b] if b in PB.index else None
    ls=sorted(linhas_b.get(b,[]),key=lambda i:-part(i))
    out.append({'n':b,'ra':row.ra,'ap':row.ap.replace('Área de Planejamento ','AP'),'pop':int(row.populacao),'dens':None if pd.isna(row.densidade_hab_km2) else int(row.densidade_hab_km2),
        'p3':row.pct_300m_a_pe,'p4':row.pct_400m_a_pe,'p5':row.pct_500m_a_pe,'p8':row.pct_800m_a_pe,'bom':row.pct_400m_a_pe_10onibus_h,
        'dist':None if pd.isna(row.dist_media_a_pe_m) else int(row.dist_media_a_pe_m),'oh':row.onibus_h_pico_medio,'desv':row.fator_desvio_medio,
        'pri':int(pr.pop_prioritaria) if pr is not None else 0,'ppri':float(pr.pct_bairro) if pr is not None else 0.0,
        'renda':None if b not in renda.index else int(round(renda[b])),'nv':nv,'bb':bb,'g':segs,'ln':ls})
cid={'pop':int(B.populacao.sum())}
w=B.populacao
for k2,c in [('p4','pct_400m_a_pe'),('bom','pct_400m_a_pe_10onibus_h'),('dist','dist_media_a_pe_m')]:
    cid[k2]=round(float((B[c]*w).sum()/w.sum()),1)
cid['pri']=int(PB.pop_prioritaria.sum())
T_=pop.sum()
cid['leg_nivel']=[round(float(pop[cls==c].sum()/T_*100),1) for c in range(5)]
bl=np.where(t>=0,(2-serv)*3+(2-t),-1); tb=pop[bl>=0].sum()
cid['leg_biv']=[round(float(pop[bl==c].sum()/tb*100),1) for c in range(9)]
cid['leg_pri']=round(float(pop[pri].sum()/T_*100),1)
rb=np.select([rat<1.3,rat<1.6,rat<2.0],[0,1,2],3); po=pop[ok]
cid['leg_desv']=[round(float(po[rb[ok]==c].sum()/T_*100),1) for c in range(4)]+[round(float(pop[~ok].sum()/T_*100),1)]
meta={'origem':[float(gx0),float(gy0),AG,GX,GY],'cidade':cid,'bairros':out}
json.dump(meta,open(os.path.join(DST,'territorio.json'),'w'),separators=(',',':'),ensure_ascii=False)
print('bairros',len(out),' KB',os.path.getsize(os.path.join(DST,'territorio.json'))//1024,' cidade',cid)
print('sem contorno:',[o['n'] for o in out if not o['g']],' sem linhas:',[o['n'] for o in out if not o['ln']])
