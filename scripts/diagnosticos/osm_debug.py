import gzip, sys, collections, numpy as np
import xml.etree.ElementTree as ET
F=sys.argv[1]; S,W,N,E=-22.985,-43.195,-22.965,-43.175   # Copacabana
nodes={}; c=collections.Counter(); tags={}; refs=[]
for ev,el in ET.iterparse(gzip.open(F),events=('start','end')):
    t=el.tag
    if ev=='start':
        if t=='way': tags={}; refs=[]
        continue
    if t=='node':
        la=float(el.get('lat')); lo=float(el.get('lon'))
        if S<la<N and W<lo<E: nodes[int(el.get('id'))]=1
        el.clear()
    elif t=='tag': tags[el.get('k')]=el.get('v')
    elif t=='nd': refs.append(int(el.get('ref')))
    elif t=='way':
        if 'highway' in tags and refs and refs[0] in nodes:
            c[(tags['highway'],tags.get('foot',''),tags.get('footway',''),tags.get('access',''),tags.get('sidewalk',''))]+=1
        el.clear()
for k,v in c.most_common(30): print(v,k)
