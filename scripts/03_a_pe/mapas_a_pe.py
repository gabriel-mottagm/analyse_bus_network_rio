import sys, os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch, Rectangle
C,OS,OUTP=sys.argv[1:4]; AGM=100.0
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL=z['meta'][:5]; nx,ny=int(nx),int(ny)
p=np.load(os.path.join(OS,'pontos.npz')); px,py=p['x'],p['y']
r=np.load(os.path.join(OUTP,'pontos_resultado.npz')); dw,de,freq=r['dw'],r['de'],r['freq']
M=pd.read_csv(os.path.join(OUTP,'pontos_mapa.csv.gz'))
S=pd.read_csv(os.path.join(OUTP,'setores_cobertura_a_pe.csv'))
NX=int(np.ceil(nx*CELL/AGM))+1; NY=int(np.ceil(ny*CELL/AGM))+1
def kidx(x,y): return (np.clip(((y-y0)//AGM).astype(int),0,NY-1))*NX+np.clip(((x-x0)//AGM).astype(int),0,NX-1)
land=np.zeros(NX*NY,bool); gi=z['cell_idx']; land[kidx(x0+(gi%nx+0.5)*CELL,y0+(gi//nx+0.5)*CELL)]=True
M['k']=kidx(px[M.p.values],py[M.p.values])
pt=np.bincount(M.k,weights=M['pop'],minlength=NX*NY); dens=pt/((AGM/1000)**2)
BG='#ffffff'; LAND='#f1efea'
def base(): rgb=np.ones((NX*NY,3)); rgb[land]=to_rgb(LAND); return rgb
def dominant(lbl,n):
    acc=np.zeros((n,NX*NY))
    for c in range(n):
        m=lbl==c; np.add.at(acc[c],M.k.values[m],M['pop'].values[m])
    return acc.argmax(0),acc.sum(0)>0
SRC='Fontes: GTFS SMTR (programação, jun/2026); IBGE Censo 2022 por setor (camada data.rio); OpenStreetMap (extrato BBBike, out/2026). Distância a pé pela rede de vias; população distribuída ao longo das vias de cada setor. Não inclui vans, trem, metrô, VLT nem barcas.'
def fig_(title,sub):
    fig=plt.figure(figsize=(17,8.6),dpi=200); ax=fig.add_axes([0.0,0.04,0.74,0.84]); ax.set_axis_off()
    fig.text(0.01,0.95,title,fontsize=18,color='#1a1a19'); fig.text(0.01,0.915,sub,fontsize=12,color='#5f5e5a')
    fig.text(0.01,0.012,SRC,fontsize=8.6,color='#5f5e5a'); return fig,ax
def alpha_mix(rgb,mask,col,a):
    rgb[mask]=a[mask,None]*col[mask]+(1-a[mask,None])*np.array(to_rgb(LAND)); return rgb
A=np.clip(dens/12000,0,1)**0.6; A[pt>0]=np.maximum(A[pt>0],0.2)
tot=M['pop'].sum()
# --- 1) nível de serviço
cols=['#e5683c','#9ec5f4','#5598e7','#256abf','#0d366b']
dom,has=dominant(M.cls.values,5)
rgb=alpha_mix(base(),has,np.array([to_rgb(c) for c in cols])[dom],A)
pct=[M[M.cls==c]['pop'].sum()/tot*100 for c in range(5)]
fig,ax=fig_('Rio de Janeiro: oferta de ônibus a até 400 m de caminhada',f'{100-pct[0]:.0f}% dos moradores têm uma parada a até 400 m a pé (eram 86% em linha reta); {pct[3]+pct[4]:.0f}% têm 10 ou mais ônibus/h no pico'.replace('.',','))
ax.imshow(rgb.reshape(NY,NX,3),origin='lower',interpolation='nearest')
lab=['Sem parada a até 400 m a pé','Menos de 4 ônibus/h','4 a 10 ônibus/h','10 a 30 ônibus/h','30 ou mais ônibus/h']
h=[Patch(color=cols[c],label=f'{lab[c]}\n{pct[c]:.1f}% da população'.replace('.',',')) for c in range(5)]+[Patch(color=LAND,label='Área sem moradores')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.745,0.82),frameon=False,fontsize=11.5,labelspacing=1.05,title='Ônibus por hora a até 400 m a pé\npico da manhã, dia útil (6h–9h)',title_fontsize=12,alignment='left')
fig.text(0.748,0.25,'Cor: classe da maioria dos moradores\nde cada quadrícula de 100 m.\nTransparência: densidade.\nFrequência: soma das linhas, no\nsentido mais frequente de cada uma.',fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
plt.savefig(os.path.join(OUTP,'mapa_a_pe_1_nivel_servico.png'),facecolor='white'); plt.close(fig)
# --- 2) bivariado renda x oferta
dec=M.dec.values; serv=np.select([M.cls.values<=2,M.cls.values==3],[0,1],2)
t=np.where(dec>0,np.select([dec<=3,dec<=7],[0,1],2),-1); lbl=np.where(t>=0,(2-serv)*3+(2-t),-1)
PAL=[['#d6d6d6','#e4acac','#c85a5a'],['#b0d5df','#ad9ea5','#985356'],['#64acbe','#627f8c','#574249']]
flat=np.array([to_rgb(PAL[i//3][i%3]) for i in range(9)])
dom,has=dominant(lbl,9); low=(pt>0)&(dens<1000)
rgb=base(); m=has&~low; rgb[m]=flat[dom[m]]; rgb[low&has]=to_rgb('#e6e3dc')
tab=pd.DataFrame({'t':t,'s':serv,'pop':M['pop']})[t>=0].groupby(['s','t'])['pop'].sum().unstack(); sh=(tab/tab.sum()*100)
fig,ax=fig_('Rio de Janeiro: renda e oferta de ônibus a pé no pico da manhã','Tons escuros: onde baixa renda e pouca oferta de ônibus coincidem')
ax.imshow(rgb.reshape(NY,NX,3),origin='lower',interpolation='nearest')
lx,ly,s=0.775,0.50,0.045
for yy in range(3):
    for xx in range(3): fig.add_artist(Rectangle((lx+xx*s*0.505,ly+yy*s),s*0.5,s*0.98,transform=fig.transFigure,color=PAL[yy][xx]))
fig.text(lx,ly-0.03,'menor renda  →',fontsize=11); fig.text(lx-0.018,ly,'menos ônibus  →',fontsize=11,rotation=90)
fig.text(lx,ly+3*s+0.06,'Renda × oferta no pico',fontsize=12.5); fig.text(lx,ly+3*s+0.025,'tercis de renda × ônibus/h a até 400 m a pé',fontsize=10.5,color='#5f5e5a')
fig.text(lx+3*s*0.505+0.008,ly+2*s+0.012,'baixa renda +\npouco ônibus',fontsize=10,color='#574249',va='bottom')
fig.text(lx+3*s*0.505+0.008,ly+0.005,'baixa renda +\nmuito ônibus',fontsize=10,color='#985356',va='bottom')
fig.text(0.748,0.30,(f"Renda: 30% mais baixa · 40% do meio · 30% mais alta.\nOferta: pouco = sem parada a 400 m a pé ou <10 ônibus/h;\nmédio = 10–30; muito = 30+ (6h–9h em dia útil).\n\n"
  f"Têm pouco ônibus: {sh.loc[0,0]:.0f}% dos 30% de renda mais baixa,\n{sh.loc[0,1]:.0f}% do meio e {sh.loc[0,2]:.0f}% dos 30% de renda mais alta.\n\nCinza bem claro: <1.000 hab/km²."),fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
plt.savefig(os.path.join(OUTP,'mapa_a_pe_2_renda_x_oferta.png'),facecolor='white'); plt.close(fig)
print('bivariado:\n',sh.round(1))
# --- 3) prioridade
pri=(dec>=1)&(dec<=3)&(serv==0)
pp=np.bincount(M.k.values[pri],weights=M['pop'].values[pri],minlength=NX*NY)
rgb=base(); rgb[pt>0]=to_rgb('#c9c6bf')
a=np.clip(pp/((AGM/1000)**2)/8000,0.25,1.0); mm=pp>0; rgb[mm]=a[mm,None]*np.array(to_rgb('#c0392b'))+(1-a[mm,None])*np.array(to_rgb(LAND))
PB=pd.read_csv(os.path.join(OUTP,'prioridade_bairros_a_pe.csv')).set_index('bairro')
bai=S.bairro.values[M.s.values]
B=pd.DataFrame({'b':bai[pri],'x':((px[M.p.values[pri]]-x0)/AGM)*M['pop'].values[pri],'y':((py[M.p.values[pri]]-y0)/AGM)*M['pop'].values[pri],'w':M['pop'].values[pri]}).groupby('b').sum()
B['x']/=B.w; B['y']/=B.w
totp=M['pop'].values[pri].sum(); lowtot=M['pop'].values[(dec>=1)&(dec<=3)].sum()
fig,ax=fig_(f'Rio de Janeiro: {totp/1e6:.2f} milhão de pessoas de baixa renda com pouca oferta de ônibus a pé'.replace('.',','),
   'Moradores dos 30% de setores de renda mais baixa sem parada a até 400 m de caminhada ou com menos de 10 ônibus/h no pico da manhã')
ax.imshow(rgb.reshape(NY,NX,3),origin='lower',interpolation='nearest')
OFF={'Santa Cruz':(-40,-45),'Maré':(70,-45),'Bangu':(0,45),'Jacarepaguá':(0,-45),'Senador Camará':(60,-40),'Guaratiba':(0,-45),'Campo Grande':(-20,40),'Paciência':(-40,45),'Complexo do Alemão':(-60,45),'Inhoaíba':(75,-60)}
for b in PB.head(10).index:
    off=OFF.get(b,(0,40))
    ax.annotate(f"{b}\n{int(PB.loc[b,'pop_prioritaria']/1000)} mil",(B.loc[b,'x'],B.loc[b,'y']),xytext=off,textcoords='offset points',fontsize=10,ha='center',va='center',
       bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='#c9c6bf',lw=0.5,alpha=0.92),arrowprops=dict(arrowstyle='-',color='#5f5e5a',lw=0.7))
h=[Patch(color='#c0392b',label='30% de renda mais baixa\nsem parada a 400 m a pé\nou com menos de 10 ônibus/h'),Patch(color='#c9c6bf',label='Demais moradores'),Patch(facecolor=LAND,edgecolor='#c9c6bf',label='Sem moradores')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.745,0.82),frameon=False,fontsize=11.5,labelspacing=1.0,title='Áreas prioritárias',title_fontsize=12,alignment='left')
fig.text(0.748,0.30,f'Intensidade do vermelho: densidade\ndessa população.\n\nRótulos: os 10 bairros com mais\nmoradores nessa situação.\n\nSão {100*totp/lowtot:.0f}% dos 30% de renda mais baixa\n(eram 41% com a distância em linha reta).',fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
plt.savefig(os.path.join(OUTP,'mapa_a_pe_3_prioridade.png'),facecolor='white'); plt.close(fig)
# --- 4) fator de desvio (caminhada ÷ linha reta até a parada mais próxima)
ddw=dw[M.p.values]; dde=de[M.p.values]; ok=(dde>100)&np.isfinite(ddw)&(ddw<5000)
ratio=np.where(ok,ddw/np.maximum(dde,1),0)
wr=np.bincount(M.k.values[ok],weights=(ratio*M['pop'].values)[ok],minlength=NX*NY); wp=np.bincount(M.k.values[ok],weights=M['pop'].values[ok],minlength=NX*NY)
fd=np.where(wp>0,wr/np.maximum(wp,1e-9),0)
ramp=['#c9d9e8','#f6c79e','#e5683c','#a8401a']
cl=np.select([fd<1.3,fd<1.6,fd<2.0],[0,1,2],3)
rgb=base(); near=(pt>0)&(wp==0); rgb[near]=to_rgb('#c9c6bf'); mm=wp>0; rgb[mm]=np.array([to_rgb(c) for c in ramp])[cl[mm]]
o=np.argsort(ratio[ok]); cw=np.cumsum(M['pop'].values[ok][o])/M['pop'].values[ok].sum(); med=ratio[ok][o][np.searchsorted(cw,.5)]
sh=[M['pop'].values[ok][(np.select([ratio[ok]<1.3,ratio[ok]<1.6,ratio[ok]<2.0],[0,1,2],3))==c].sum()/M['pop'].values[ok].sum()*100 for c in range(4)]
fig,ax=fig_('Rio de Janeiro: quanto a caminhada até o ônibus é mais longa que a linha reta',
   f'Fator de desvio até a parada mais próxima. Mediana da cidade: {med:.2f}. Valores altos indicam morros, vias expressas, linhas férreas e quadras fechadas'.replace('.',',',1) if False else f'Fator de desvio até a parada mais próxima (mediana da cidade: {str(round(med,2)).replace(".",",")}). Valores altos indicam morros, vias expressas, linhas férreas e quadras fechadas')
ax.imshow(rgb.reshape(NY,NX,3),origin='lower',interpolation='nearest')
labs=['Menos de 1,3 (caminho quase direto)','1,3 a 1,6','1,6 a 2,0','2,0 ou mais (desvio grande)']
h=[Patch(color=ramp[i],label=f'{labs[i]}\n{sh[i]:.0f}% dos moradores'.replace('.',',')) for i in range(4)]+[Patch(color='#c9c6bf',label='Parada a menos de 100 m'),Patch(facecolor=LAND,edgecolor='#c9c6bf',label='Sem moradores')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.745,0.82),frameon=False,fontsize=11.5,labelspacing=1.0,title='Distância a pé ÷ distância em linha reta',title_fontsize=12,alignment='left')
fig.text(0.748,0.25,'Média ponderada pela população\nem quadrículas de 100 m. Moradores\na menos de 100 m da parada (em\nlinha reta) ficam de fora do cálculo.',fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
plt.savefig(os.path.join(OUTP,'mapa_a_pe_4_desvio.png'),facecolor='white'); plt.close(fig)
print('pop prioritária',round(totp),' desvio mediano',round(med,2),[round(x,1) for x in sh])
