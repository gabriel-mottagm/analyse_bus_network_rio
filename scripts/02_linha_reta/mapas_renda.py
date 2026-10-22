import numpy as np, pandas as pd, sys, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch, Rectangle
C,O=sys.argv[1],sys.argv[2]; AG=5; CELL=20.0
g=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny=g['meta'][:4]; nx,ny=int(nx),int(ny)
z=np.load(os.path.join(O,'celulas.npz')); ci,cp,d,freq,co=z['ci'],z['cp'],z['d'],z['freq'],z['co']
S=pd.read_csv(os.path.join(O,'setores_cobertura.csv'))
renda=S.renda_media_responsavel.values; semdado=(renda<=0)
# decis de renda ponderados por população (nível setor)
Sp=S[(S.populacao>0)&(~semdado)].sort_values('renda_media_responsavel')
cum=Sp.populacao.cumsum()/Sp.populacao.sum()
dec=np.full(len(S),-1); dec[Sp.index]=np.minimum((cum*10).astype(int)+1,10).values
lim=Sp.groupby(dec[Sp.index]).renda_media_responsavel.agg(['min','max'])
print(lim.round(0))
dcell=dec[co]
serv=np.select([(d>400)|(freq<10),freq<30],[0,1],2)          # 0 baixa,1 média,2 alta
# agrega em quadrículas de 100 m: classe da maioria
X,Y=(ci%nx)//AG,(ci//nx)//AG; NX,NY=nx//AG+1,ny//AG+1; k=Y*NX+X
land=np.zeros(NX*NY,bool); gi=g['cell_idx']; land[((gi//nx)//AG)*NX+(gi%nx)//AG]=True
pt=np.bincount(k,weights=cp,minlength=NX*NY); dens=pt/((AG*CELL/1000)**2)
LOW=1000
def dominant(lbl,n):
    acc=np.zeros((n,NX*NY))
    for c in range(n):
        m=lbl==c; np.add.at(acc[c],k[m],cp[m])
    return acc.argmax(0), acc
BG='#ffffff'; LOWC='#f1efea'
def base():
    rgb=np.ones((NX*NY,3)); rgb[land]=to_rgb(BG); return rgb
def show(rgb,title,sub,fn,handles,legtitle,note,extra=None):
    fig=plt.figure(figsize=(17,8.6),dpi=200); ax=fig.add_axes([0.0,0.04,0.74,0.84])
    ax.imshow(rgb.reshape(NY,NX,3),origin='lower',interpolation='nearest'); ax.set_axis_off()
    if extra: extra(fig,ax)
    if handles: fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(0.745,0.82),frameon=False,fontsize=11.5,labelspacing=1.0,title=legtitle,title_fontsize=12,alignment='left')
    fig.text(0.748,0.30,note,fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
    fig.text(0.01,0.95,title,fontsize=18,color='#1a1a19'); fig.text(0.01,0.915,sub,fontsize=12,color='#5f5e5a')
    fig.text(0.01,0.012,'Fontes: GTFS SMTR (programação, jun/2026); IBGE Censo 2022 por setor censitário (camada data.rio). População distribuída uniformemente em cada setor; distância em linha reta. Não inclui vans, trem, metrô, VLT nem barcas.',fontsize=9,color='#5f5e5a')
    plt.savefig(os.path.join(O,fn),facecolor='white'); plt.close(fig)
lowmask=(pt>0)&(dens<LOW); pctlow=pt[lowmask].sum()/pt.sum()*100
# ---- Mapa 1: renda (quintis)
q=np.where(dcell>0,(dcell-1)//2,-1)
domq,accq=dominant(q,5); has=(accq.sum(0)>0)
ramp=['#fde3cf','#f9b98a','#ef8a4c','#c75d22','#8a3a10']
rgb=base(); rgb[has&~lowmask]=np.array([to_rgb(c) for c in ramp])[domq[has&~lowmask]]; rgb[lowmask]=to_rgb(LOWC)
qlab=[f"{int(lim.loc[2*i+1,'min']):,}".replace(',','.')+' a '+f"{int(lim.loc[2*i+2,'max']):,}".replace(',','.') for i in range(5)]
names=['20% de renda mais baixa','2º quinto','3º quinto','4º quinto','20% de renda mais alta']
h=[Patch(color=ramp[i],label=f'{names[i]}\nR$ {qlab[i]}') for i in range(5)]+[Patch(color=LOWC,label=f'Baixa densidade (<{LOW:,} hab/km²)'.replace(',','.')),Patch(facecolor=BG,edgecolor='#c9c6bf',label='Sem moradores')]
show(rgb,'Rio de Janeiro: renda média do responsável pelo domicílio','Quintos da população, do setor censitário de renda mais baixa ao de renda mais alta',
     'mapa_1_renda.png',h,'Renda média mensal do responsável',f'Cada quinto reúne ~1,24 milhão de\npessoas. Quadrículas de 100 m com\nmenos de {LOW:,} hab/km² em cinza\n({str(round(pctlow,1)).replace(".",",")}% da população).'.replace('1,000','1.000'))
# ---- Mapa 2: bivariado renda (tercis) x oferta (3 classes)
t=np.where(dcell>0,np.select([dcell<=3,dcell<=7],[0,1],2),-1)    # 0 = 30% de renda mais baixa, 1 = meio (40%), 2 = 30% de renda mais alta
xr=2-t                                                            # x: 0 renda alta ... 2 renda baixa
ys=2-serv                                                         # y: 0 oferta alta ... 2 baixa
lbl=np.where(t>=0,ys*3+xr,-1)
domb,accb=dominant(lbl,9); has=(accb.sum(0)>0)
PAL=[['#d6d6d6','#e4acac','#c85a5a'],['#b0d5df','#ad9ea5','#985356'],['#64acbe','#627f8c','#574249']]
flat=np.array([to_rgb(PAL[i//3][i%3]) for i in range(9)])
rgb=base(); rgb[has&~lowmask]=flat[domb[has&~lowmask]]; rgb[lowmask]=to_rgb(LOWC)
# tabela de população por célula do bivariado
tab=pd.DataFrame({'renda':t,'oferta':serv,'pop':cp})[t>=0].groupby(['oferta','renda'])['pop'].sum().unstack()
share=(tab/tab.sum()*100).round(1); print('bivariado % dentro de cada faixa de renda:\n',share)
def legend_bi(fig,ax):
    lx,ly,s=0.775,0.50,0.045
    for yy in range(3):
        for xx in range(3):
            fig.add_artist(Rectangle((lx+xx*s*0.505,ly+yy*s),s*0.5,s*0.98,transform=fig.transFigure,color=PAL[yy][xx]))
    fig.text(lx,ly-0.03,'menor renda  →',fontsize=11,color='#1a1a19')
    fig.text(lx-0.018,ly,'menos ônibus  →',fontsize=11,color='#1a1a19',rotation=90)
    fig.text(lx,ly+3*s+0.06,'Renda × oferta no pico',fontsize=12.5,color='#1a1a19')
    fig.text(lx,ly+3*s+0.025,'tercis de renda × ônibus/h a até 400 m',fontsize=10.5,color='#5f5e5a')
    fig.text(lx+3*s*0.505+0.008,ly+2*s+0.012,'baixa renda +\npouco ônibus',fontsize=10,color='#574249',va='bottom')
    fig.text(lx+3*s*0.505+0.008,ly+0.005,'baixa renda +\nmuito ônibus',fontsize=10,color='#985356',va='bottom')
    fig.text(lx-0.005,ly+3*s+0.0,'',fontsize=1)
sp=share
note=(f"Renda: 30% mais baixa · 40% do meio · 30% mais alta.\n"
      f"Oferta: pouco = sem parada ou <10 ônibus/h; médio = 10–30;\nmuito = 30+ (6h–9h em dia útil).\n\n"
      f"Têm pouco ônibus: {sp.loc[0,0]:.0f}% dos 30% de renda mais baixa,\n{sp.loc[0,1]:.0f}% do meio e {sp.loc[0,2]:.0f}% dos 30% de renda mais alta.\n\n"
      f"Cinza bem claro: <{LOW:,} hab/km².").replace(',','.')
fig_note=note
show(rgb,'Rio de Janeiro: renda e oferta de ônibus no pico da manhã','Tons escuros: onde baixa renda e pouca oferta de ônibus coincidem',
     'mapa_2_renda_x_oferta.png',None,None,fig_note,legend_bi)
# ---- Mapa 3: prioridade (30% de renda mais baixa E pouca oferta)
pri=(dcell>=1)&(dcell<=3)&(serv==0)
pp=np.bincount(k[pri],weights=cp[pri],minlength=NX*NY)
rgb=base(); pop_any=pt>0
grey=np.array(to_rgb('#c9c6bf')); rgb[pop_any]=grey
show_mask=pp>0
a=np.clip(pp/((AG*CELL/1000)**2)/8000,0.25,1.0)
red=np.array(to_rgb('#c0392b'))
rgb[show_mask]=a[show_mask,None]*red+(1-a[show_mask,None])*to_rgb(BG)
PRI=pd.DataFrame({'own':co[pri],'pop':cp[pri],'semparada':np.where(d[pri]>400,cp[pri],0)})
PB=PRI.groupby(PRI.own.map(S.bairro))[['pop','semparada']].sum().sort_values('pop',ascending=False)
PB.columns=['pop_prioritaria','dos_quais_sem_parada_400m']; PB=PB.round(0).astype(int)
PB['pop_bairro']=S.groupby('bairro').populacao.sum().reindex(PB.index)
PB['pct_bairro']=(100*PB.pop_prioritaria/PB.pop_bairro).round(1)
PB.rename_axis('bairro').reset_index().to_csv(os.path.join(O,'prioridade_bairros.csv'),index=False)
totp=cp[pri].sum(); print('pop prioritária',round(totp)); print(PB.head(12))
# rótulos dos 10 bairros com mais população prioritária (centróide ponderado)
cx=(ci%nx); cy=(ci//nx)
B=pd.DataFrame({'b':S.bairro.values[co[pri]],'x':cx[pri]*cp[pri],'y':cy[pri]*cp[pri],'p':cp[pri]}).groupby('b').sum()
B['x']/=B.p; B['y']/=B.p
top=PB.head(10).index
OFF={'Maré':(70,-45),'Complexo do Alemão':(-60,45),'Campo Grande':(-30,-30),'Senador Camará':(45,-40),'Bangu':(0,40),'Inhoaíba':(75,-70),'Paciência':(-10,45),'Santa Cruz':(-40,-40),'Guaratiba':(0,-40),'Jacarepaguá':(0,-40)}
def labels(fig,ax):
    for b in top:
        off=OFF.get(b,(0,0))
        ax.annotate(f"{b}\n{int(PB.loc[b,'pop_prioritaria']/1000)} mil",(B.loc[b,'x']/AG,B.loc[b,'y']/AG),xytext=off,textcoords='offset points',
            fontsize=10,ha='center',va='center',color='#1a1a19',bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='#c9c6bf',lw=0.5,alpha=0.92),
            arrowprops=dict(arrowstyle='-',color='#5f5e5a',lw=0.7) if off!=(0,0) else None)
h=[Patch(color='#c0392b',label='30% de renda mais baixa\nsem parada a 400 m\nou com menos de 10 ônibus/h'),Patch(color='#c9c6bf',label='Demais moradores'),Patch(facecolor=BG,edgecolor='#c9c6bf',label='Sem moradores')]
show(rgb,f'Rio de Janeiro: {round(totp/1000)} mil pessoas de baixa renda com pouca oferta de ônibus',
     'Moradores dos 30% de setores de renda mais baixa sem parada a até 400 m ou com menos de 10 ônibus/h no pico da manhã',
     'mapa_3_prioridade.png',h,'Áreas prioritárias',
     f'Intensidade do vermelho: densidade\ndessa população.\n\nRótulos: os 10 bairros com mais\nmoradores nessa situação.\n\nSão {100*totp/cp[(dcell>=1)&(dcell<=3)].sum():.0f}% dos 30% de renda mais baixa\n(contra {100*cp[(dcell>=8)&(serv==0)].sum()/cp[dcell>=8].sum():.0f}% dos 30% de renda mais alta).',labels)
