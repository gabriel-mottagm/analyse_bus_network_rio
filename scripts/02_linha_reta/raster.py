# Rasteriza setores numa grade de CELL m; população distribuída uniformemente no setor
import json, numpy as np, pandas as pd, sys, os
from matplotlib.path import Path
SET, O = sys.argv[1], sys.argv[2]; CELL=20.0
LAT0, LON0 = -22.9, -43.45
KX = np.cos(np.radians(LAT0))*111320.0; KY = 110574.0
def proj(lon,lat): return (np.asarray(lon)-LON0)*KX, (np.asarray(lat)-LAT0)*KY
g=json.load(open(SET)); F=g['features']
props=pd.DataFrame([f['properties'] for f in F])
polys=[]  # list of (exterior, [holes]) per feature
xs=[];ys=[]
for f in F:
    gm=f['geometry']; parts=gm['coordinates'] if gm['type']=='MultiPolygon' else [gm['coordinates']]
    pp=[]
    for rings in parts:
        R=[np.column_stack(proj(np.array(r)[:,0],np.array(r)[:,1])) for r in rings]
        pp.append(R); xs.append(R[0][:,0]); ys.append(R[0][:,1])
    polys.append(pp)
X=np.concatenate(xs); Y=np.concatenate(ys)
x0,y0=np.floor(X.min()/CELL)*CELL, np.floor(Y.min()/CELL)*CELL
nx=int(np.ceil((X.max()-x0)/CELL))+1; ny=int(np.ceil((Y.max()-y0)/CELL))+1
print("grade",nx,ny,nx*ny)
owner=np.full(ny*nx,-1,dtype=np.int32)
area_cells=np.zeros(len(F),dtype=np.int64)
for i,pp in enumerate(polys):
    for R in pp:
        ex=R[0]; ix0=int((ex[:,0].min()-x0)//CELL); ix1=int((ex[:,0].max()-x0)//CELL)+1
        iy0=int((ex[:,1].min()-y0)//CELL); iy1=int((ex[:,1].max()-y0)//CELL)+1
        gx,gy=np.meshgrid(np.arange(ix0,ix1+1),np.arange(iy0,iy1+1))
        cx=x0+(gx.ravel()+0.5)*CELL; cy=y0+(gy.ravel()+0.5)*CELL; pts=np.column_stack([cx,cy])
        m=Path(ex).contains_points(pts)
        for h in R[1:]: m&=~Path(h).contains_points(pts)
        idx=(gy.ravel()*nx+gx.ravel())[m]
        owner[idx]=i
cnt=np.bincount(owner[owner>=0],minlength=len(F))
# setores sem célula: atribui ao centróide
pop=props.total_de_p.values.astype(float)
miss=np.where(cnt==0)[0]; print("setores sem célula:",len(miss)," pop:",pop[miss].sum())
extra_idx=[];extra_own=[]
for i in miss:
    ex=polys[i][0][0]; cx,cy=ex[:,0].mean(),ex[:,1].mean()
    extra_idx.append(int((cy-y0)//CELL)*nx+int((cx-x0)//CELL)); extra_own.append(i)
cell_idx=np.concatenate([np.where(owner>=0)[0],np.array(extra_idx,dtype=np.int64)])
cell_own=np.concatenate([owner[owner>=0],np.array(extra_own,dtype=np.int32)])
cnt=np.bincount(cell_own,minlength=len(F))
cell_pop=pop[cell_own]/cnt[cell_own]
print("pop rasterizada:",cell_pop.sum()," original:",pop.sum())
props['area_km2']=cnt*CELL*CELL/1e6
np.savez_compressed(os.path.join(O,'grade.npz'),cell_idx=cell_idx,cell_own=cell_own,cell_pop=cell_pop,meta=np.array([x0,y0,nx,ny,CELL,LAT0,LON0,KX,KY]))
props.drop(columns=['SHAPE__Length','SHAPE__Area']).to_csv(os.path.join(O,'setores_atributos.csv'),index=False)
print("área total km2:",props.area_km2.sum().round(1))
