import gzip, sys, os, numpy as np, pandas as pd
import xml.etree.ElementTree as ET
F,C,O=sys.argv[1],sys.argv[2],sys.argv[3]
ids=[];la=[];lo=[]; bw=[]  # buildings: (way_id, building, levels, refs)
cur=None; tags={}; refs=[]
for ev,el in ET.iterparse(gzip.open(F),events=('start','end')):
    t=el.tag
    if ev=='start':
        if t=='way': tags={}; refs=[]
        elif t=='node': tags={}
        continue
    if t=='node':
        ids.append(int(el.get('id'))); la.append(float(el.get('lat'))); lo.append(float(el.get('lon'))); el.clear()
    elif t=='tag': tags[el.get('k')]=el.get('v')
    elif t=='nd': refs.append(int(el.get('ref')))
    elif t=='way':
        if 'building' in tags: bw.append((int(el.get('id')),tags['building'],tags.get('building:levels',''),refs[:-1] if len(refs)>1 and refs[0]==refs[-1] else refs))
        el.clear()
ids=np.array(ids); la=np.array(la); lo=np.array(lo); o=np.argsort(ids); ids,la,lo=ids[o],la[o],lo[o]
z=np.load(os.path.join(C,'grade.npz')); x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY=z['meta']; nx=int(nx)
rows=[]
for wid,b,lv,r in bw:
    r=np.array(r); p=np.searchsorted(ids,r); p=p[(p<len(ids))]; p=p[ids[p]==r[:len(p)]] if len(p)==len(r) else p[np.isin(ids[p],r)]
    if len(p)<3: continue
    X=(lo[p]-LON0)*KX; Y=(la[p]-LAT0)*KY
    A=0.5*abs(np.dot(X,np.roll(Y,1))-np.dot(Y,np.roll(X,1)))
    rows.append((wid,b,lv,X.mean(),Y.mean(),A))
B=pd.DataFrame(rows,columns=['way_id','building','levels','x','y','area_m2'])
# setor de cada edificação via grade
cid=((B.y-y0)//CELL).astype(int)*nx+((B.x-x0)//CELL).astype(int)
own=np.full(int(nx)*int(ny),-1,dtype=np.int32); own[z['cell_idx']]=z['cell_own']
B['setor_idx']=own[np.clip(cid,0,len(own)-1)]
B.to_csv(os.path.join(O,'edificacoes_osm.csv'),index=False)
S=pd.read_csv(os.path.join(C,'setores_atributos.csv'))
g=B[B.setor_idx>=0].groupby('setor_idx').agg(n=('way_id','size'),area=('area_m2','sum'))
S=S.join(g); S[['n','area']]=S[['n','area']].fillna(0)
P=S[S.total_de_p>0]; tot=P.total_de_p.sum()
print('edificações:',len(B),' dentro do município:',(B.setor_idx>=0).sum(),' área total km2:',round(B.area_m2.sum()/1e6,1))
print('setores com moradores:',len(P),' sem nenhuma edificação:',(P.n==0).sum(),f' ({P[P.n==0].total_de_p.sum()/tot*100:.1f}% da pop)')
print('pop em setores com <5 edificações: %.1f%%' % (P[P.n<5].total_de_p.sum()/tot*100))
P=P.assign(ratio=P.n/P.total_de_d.replace(0,np.nan))
print('edificações por domicílio (mediana) por AP:'); print(P.groupby('ap').ratio.median().round(2))
cov=P.groupby('ap').apply(lambda d:(d[d.n==0].total_de_p.sum()/d.total_de_p.sum()*100).round(1)); print('% pop em setores sem edificação, por AP:'); print(cov)
fav=P.sort_values('total_de_p',ascending=False)
for bai in ['Maré','Complexo do Alemão','Rocinha','Santa Cruz','Campo Grande','Copacabana','Barra da Tijuca','Jacarezinho','Cidade de Deus']:
    d=P[P.bairro==bai]; print(f'{bai}: setores {len(d)}, sem edif. {int((d.n==0).sum())}, edif/domicílio {(d.n.sum()/d.total_de_d.sum()):.2f}')
