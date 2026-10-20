# 1) Lê o OSM XML, monta o grafo de caminhada e salva arestas + atributos de alocação
import gzip, sys, os, numpy as np
import xml.etree.ElementTree as ET
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
F,C,O=sys.argv[1],sys.argv[2],sys.argv[3]
EXC={'motorway','motorway_link','construction','proposed','abandoned','raceway','bus_guideway','busway','platform','rest_area','services','elevator','emergency_bay','escape','no','razed','disused'}
NOALLOC={'trunk','trunk_link','primary_link','secondary_link','tertiary_link','cycleway','bridleway','corridor'}
ids=[];la=[];lo=[]; eu=[];ev=[];ea=[]; tags={}; refs=[]
for evn,el in ET.iterparse(gzip.open(F),events=('start','end')):
    t=el.tag
    if evn=='start':
        if t=='way': tags={}; refs=[]
        continue
    if t=='node': ids.append(int(el.get('id'))); la.append(float(el.get('lat'))); lo.append(float(el.get('lon'))); el.clear()
    elif t=='tag': tags[el.get('k')]=el.get('v')
    elif t=='nd': refs.append(int(el.get('ref')))
    elif t=='way':
        h=tags.get('highway')
        if h and h not in EXC and tags.get('foot') not in ('no','private','use_sidepath') and tags.get('area')!='yes' and tags.get('access') not in ('no',) or (h and tags.get('foot') in ('yes','designated','permissive') and h not in ('construction','proposed')):
            alloc = h not in NOALLOC and tags.get('footway') not in ('sidewalk','crossing') and tags.get('service') not in ('parking_aisle','drive-through') and tags.get('tunnel')!='yes' and tags.get('bridge')!='yes'
            for a,b in zip(refs[:-1],refs[1:]): eu.append(a); ev.append(b); ea.append(alloc)
        el.clear()
ids=np.array(ids); o=np.argsort(ids); ids=ids[o]; la=np.array(la)[o]; lo=np.array(lo)[o]
eu=np.array(eu); ev=np.array(ev); ea=np.array(ea)
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']
used=np.unique(np.concatenate([eu,ev])); pu=np.searchsorted(ids,used); ok=(pu<len(ids))&(ids[np.minimum(pu,len(ids)-1)]==used)
used=used[ok]; pu=pu[ok]
X=(lo[pu]-LON0)*KX; Y=(la[pu]-LAT0)*KY
iu=np.searchsorted(used,eu); iv=np.searchsorted(used,ev)
good=(iu<len(used))&(iv<len(used)); good&=(used[np.minimum(iu,len(used)-1)]==eu)&(used[np.minimum(iv,len(used)-1)]==ev)&(iu!=iv)
iu,iv,ea=iu[good],iv[good],ea[good]
L=np.hypot(X[iu]-X[iv],Y[iu]-Y[iv])
N=len(used)
G=coo_matrix((L,(iu,iv)),shape=(N,N)).tocsr(); G=G.maximum(G.T)
nc,lab=connected_components(G,directed=False)
sz=np.bincount(lab); main=sz.argmax()
print(f"nós {N:,}  arestas {len(L):,}  km de vias {L.sum()/1000:,.0f}  (alocáveis {L[ea].sum()/1000:,.0f} km)")
print(f"componentes {nc:,}; principal com {sz[main]:,} nós ({sz[main]/N*100:.1f}%); 2º {np.sort(sz)[-2]:,}; 3º {np.sort(sz)[-3]:,}")
np.savez_compressed(os.path.join(O,'grafo.npz'),X=X,Y=Y,iu=iu,iv=iv,L=L,ea=ea,lab=lab,main=main)
