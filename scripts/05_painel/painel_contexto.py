# Camadas de fundo: contorno da cidade, limites aproximados de bairro, vias principais e trilhos (OSM)
import gzip, sys, os, json, numpy as np, pandas as pd
import xml.etree.ElementTree as ET
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.path import Path
C,OSMF,DST=sys.argv[1:4]
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']; nx,ny=int(nx),int(ny)
def rdp(a,eps):
    if len(a)<3: return a
    st=[(0,len(a)-1)]; keep=np.zeros(len(a),bool); keep[0]=keep[-1]=True
    while st:
        i,j=st.pop(); p,q=a[i],a[j]; seg=a[i+1:j]
        if len(seg)==0: continue
        d=q-p; n=np.hypot(*d)
        v=seg-p; dist=np.abs(d[0]*v[:,1]-d[1]*v[:,0])/n if n>0 else np.hypot(v[:,0],v[:,1])
        k=np.argmax(dist)
        if dist[k]>eps: keep[i+1+k]=True; st+=[(i,i+1+k),(i+1+k,j)]
    return a[keep]
F=3  # 60 m
own=np.full(nx*ny,-1,dtype=np.int32); own[z['cell_idx']]=z['cell_own']; own=own.reshape(ny,nx)
NY,NX=ny//F,nx//F; own=own[:NY*F,:NX*F].reshape(NY,F,NX,F)
S=pd.read_csv(os.path.join(C,'setores_atributos.csv'))
bai_codes,bai_names=pd.factorize(S.bairro)
lab=np.full(own.shape,-1); m=own>=0; lab[m]=bai_codes[own[m]]
# moda por bloco 3x3
lab=lab.transpose(0,2,1,3).reshape(NY,NX,F*F)
def mode(v):
    v=v[v>=0]; return np.bincount(v).argmax() if len(v) else -1
B=np.apply_along_axis(mode,2,lab)
gx=x0+(np.arange(NX)+0.5)*CELL*F; gy=y0+(np.arange(NY)+0.5)*CELL*F
def contours(mask,eps):
    fig=plt.figure(); cs=plt.contour(gx,gy,np.pad(mask.astype(float),0),levels=[0.5]); plt.close(fig)
    out=[]
    for seg in cs.allsegs[0]:
        if len(seg)>=4: out.append(rdp(np.asarray(seg),eps))
    return out
land=contours(B>=0,25)
land=[s for s in land if len(s)>3]
bairros=[]
for k in range(len(bai_names)):
    for s in contours(B==k,25):
        if len(s)>3: bairros.append(s)
print('anéis cidade',len(land),' segmentos bairro',len(bairros),' pts',sum(len(s) for s in bairros))
# rótulos de bairro: centróide ponderado pela população (grade 20 m)
ci,co,cp=z['cell_idx'],z['cell_own'],z['cell_pop']
cx=x0+(ci%nx+0.5)*CELL; cy=y0+(ci//nx+0.5)*CELL
D=pd.DataFrame({'b':S.bairro.values[co],'x':cx*cp,'y':cy*cp,'p':cp}).groupby('b').sum()
D=D[D.p>0]; D['x']/=D.p; D['y']/=D.p
labels=[[n,int(r.x),int(r.y),int(r.p)] for n,r in D.sort_values('p',ascending=False).iterrows()]
# vias e trilhos (OSM)
ids=[];la=[];lo=[]; ways=[]; tags={}; refs=[]
for ev,el in ET.iterparse(gzip.open(OSMF),events=('start','end')):
    t=el.tag
    if ev=='start':
        if t=='way': tags={}; refs=[]
        continue
    if t=='node': ids.append(int(el.get('id'))); la.append(float(el.get('lat'))); lo.append(float(el.get('lon'))); el.clear()
    elif t=='tag': tags[el.get('k')]=el.get('v')
    elif t=='nd': refs.append(int(el.get('ref')))
    elif t=='way':
        h=tags.get('highway'); r=tags.get('railway')
        kind=None
        if h in ('motorway','trunk'): kind=0
        elif h=='primary': kind=1
        elif h=='secondary': kind=2
        elif r in ('rail','subway','light_rail') and tags.get('service') is None and tags.get('usage')!='industrial': kind=3
        if kind is not None: ways.append((kind,refs[:]))
        el.clear()
ids=np.array(ids); o=np.argsort(ids); ids=ids[o]; X=(np.array(lo)[o]-LON0)*KX; Y=(np.array(la)[o]-LAT0)*KY
roads={0:[],1:[],2:[],3:[]}
xmin,xmax,ymin,ymax=x0-3000,x0+nx*CELL+3000,y0-3000,y0+ny*CELL+3000
for kind,r in ways:
    r=np.array(r); p=np.searchsorted(ids,r); ok=(p<len(ids)); p=p[ok]; r=r[ok]; p=p[ids[p]==r]
    if len(p)<2: continue
    a=np.column_stack([X[p],Y[p]])
    if a[:,0].max()<xmin or a[:,0].min()>xmax or a[:,1].max()<ymin or a[:,1].min()>ymax: continue
    roads[kind].append(rdp(a,8 if kind<3 else 10))
print({k:(len(v),sum(len(s) for s in v)) for k,v in roads.items()})
enc=lambda segs:[np.round(s).astype(int).ravel().tolist() for s in segs]
out={'origem':[float(LON0),float(LAT0),float(KX),float(KY)],'cidade':enc(land),'bairros':enc(bairros),
     'vias':{'expressas':enc(roads[0]),'principais':enc(roads[1]),'secundarias':enc(roads[2]),'trilhos':enc(roads[3])},'rotulos':labels}
json.dump(out,open(os.path.join(DST,'contexto.json'),'w'),separators=(',',':'))
print('contexto.json KB',os.path.getsize(os.path.join(DST,'contexto.json'))//1024)
