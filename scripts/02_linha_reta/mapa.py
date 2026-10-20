import numpy as np, sys, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch
C,O=sys.argv[1],sys.argv[2]; AG=5  # 5x20m = 100 m
g=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL=g['meta'][:5]; nx,ny=int(nx),int(ny)
z=np.load(os.path.join(O,'celulas.npz')); ci,cp,d,freq=z['ci'],z['cp'],z['d'],z['freq']
cls=np.select([d>400,freq<4,freq<10,freq<30],[0,1,2,3],4)
X,Y=(ci%nx)//AG,(ci//nx)//AG; NX,NY=nx//AG+1,ny//AG+1; k=Y*NX+X
popk=np.zeros((5,NX*NY))
for c in range(5): np.add.at(popk[c],k[cls==c],cp[cls==c])
pt=popk.sum(0); dom=popk.argmax(0)
land=np.zeros(NX*NY,bool); gi=g['cell_idx']; land[((gi//nx)//AG)*NX+(gi%nx)//AG]=True
cols=['#e5683c','#9ec5f4','#5598e7','#256abf','#0d366b']; bg=np.array(to_rgb('#e6e4df'))
dens=pt/((AG*CELL/1000)**2)                     # hab/km²
a=np.clip(dens/12000,0,1)**0.6; a[pt>0]=np.maximum(a[pt>0],0.18)
rgb=np.ones((NX*NY,3)); rgb[land]=bg
C_=np.array([to_rgb(c) for c in cols])[dom]
rgb=np.where((pt>0)[:,None], a[:,None]*C_+(1-a[:,None])*bg, rgb)
img=rgb.reshape(NY,NX,3)
fig=plt.figure(figsize=(17,8.6),dpi=200); ax=fig.add_axes([0.0,0.02,0.74,0.86])
ax.imshow(img,origin='lower',interpolation='nearest'); ax.set_axis_off()
tot=cp.sum(); pct=[cp[cls==c].sum()/tot*100 for c in range(5)]
lab=['Sem parada a até 400 m','Menos de 4 ônibus/h','4 a 10 ônibus/h','10 a 30 ônibus/h','30 ou mais ônibus/h']
h=[Patch(color=cols[c],label=f'{lab[c]}\n{pct[c]:.1f}% da população') for c in range(5)]+[Patch(color='#e6e4df',label='Área sem moradores')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.745,0.80),frameon=False,fontsize=11.5,labelspacing=1.1,
  title='Ônibus por hora a até 400 m\npico da manhã, dia útil (6h–9h)',title_fontsize=12,alignment='left')
fig.text(0.748,0.26,'Cor: classe da maioria dos moradores\nde cada quadrícula de 100 m.\nTransparência: densidade (mais\nclaro = menos moradores).\nFrequência: soma das linhas, no\nsentido mais frequente de cada uma.',fontsize=10,color='#5f5e5a',va='top',linespacing=1.4)
fig.text(0.01,0.95,'Rio de Janeiro: onde mora a população e quanto ônibus passa perto',fontsize=18,color='#1a1a19')
fig.text(0.01,0.915,'85% dos moradores têm uma parada a até 400 m em linha reta; 74% têm 10 ou mais ônibus por hora no pico',fontsize=12,color='#5f5e5a')
fig.text(0.01,0.01,'Fontes: GTFS SMTR (programação, jun/2026); IBGE Censo 2022 por setor censitário (camada data.rio). População distribuída uniformemente em cada setor (grade de 20 m). Não inclui vans, trem, metrô, VLT nem barcas.',fontsize=9,color='#5f5e5a')
plt.savefig(os.path.join(O,'mapa_nivel_servico.png'),facecolor='white')
print([round(p,1) for p in pct], round(sum(pct[3:]),1))
