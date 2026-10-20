import gzip, sys, os, numpy as np, pandas as pd
import xml.etree.ElementTree as ET
F,C=sys.argv[1],sys.argv[2]
EXC={'motorway','motorway_link','construction','proposed','abandoned','raceway','bus_guideway','busway','platform','rest_area','services'}
ids=[];la=[];lo=[]; used=[]; tags={}; refs=[]
for ev,el in ET.iterparse(gzip.open(F),events=('start','end')):
    t=el.tag
    if ev=='start':
        if t=='way': tags={}; refs=[]
        continue
    if t=='node': ids.append(int(el.get('id'))); la.append(float(el.get('lat'))); lo.append(float(el.get('lon'))); el.clear()
    elif t=='tag': tags[el.get('k')]=el.get('v')
    elif t=='nd': refs.append(int(el.get('ref')))
    elif t=='way':
        h=tags.get('highway')
        if h and h not in EXC and tags.get('foot') not in ('no','private') and tags.get('area')!='yes': used.extend(refs)
        el.clear()
ids=np.array(ids); o=np.argsort(ids); ids=ids[o]; la=np.array(la)[o]; lo=np.array(lo)[o]
u=np.unique(np.array(used)); p=np.searchsorted(ids,u); p=p[(p<len(ids))&(ids[np.minimum(p,len(ids)-1)]==u)]
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']; nx=int(nx); ny=int(ny)
X=(lo[p]-LON0)*KX; Y=(la[p]-LAT0)*KY
cid=((Y-y0)//CELL).astype(int)*nx+((X-x0)//CELL).astype(int); ok=(cid>=0)&(cid<nx*ny)
own=np.full(nx*ny,-1,dtype=np.int32); own[z['cell_idx']]=z['cell_own']
so=own[cid[ok]]; cnt=np.bincount(so[so>=0],minlength=own.max()+1)
S=pd.read_csv(os.path.join(C,'setores_atributos.csv')); S['nos']=cnt[:len(S)]
P=S[S.total_de_p>0]; tot=P.total_de_p.sum()
print('nós da rede de caminhada:',len(p))
print('setores com moradores sem nenhum nó de rua: %d (%.1f%% da pop)'%((P.nos==0).sum(),P[P.nos==0].total_de_p.sum()/tot*100))
print('pop em setores com <3 nós: %.1f%%'%(P[P.nos<3].total_de_p.sum()/tot*100))
for b in ['Maré','Complexo do Alemão','Rocinha','Cidade de Deus','Jacarezinho','Santa Cruz','Copacabana']:
    d=P[P.bairro==b]; print(f'{b}: setores {len(d)}, sem nó {int((d.nos==0).sum())}, nós/ha {d.nos.sum()/d.area_km2.sum()/100:.1f}')
