import gzip, sys, collections
import xml.etree.ElementTree as ET
f=sys.argv[1]; n=collections.Counter(); hw=collections.Counter(); bt=collections.Counter(); lv=0; ts=None; rel_b=0
cur=None; tags={}
for ev,el in ET.iterparse(gzip.open(f),events=('start','end')):
    t=el.tag
    if ev=='start':
        if t in('node','way','relation'): cur=t; tags={}
        if t=='osm': pass
        continue
    if t=='tag': tags[el.get('k')]=el.get('v')
    elif t in('node','way','relation'):
        n[t]+=1
        if t=='way':
            if 'highway' in tags: hw[tags['highway']]+=1
            if 'building' in tags:
                bt[tags['building']]+=1
                if 'building:levels' in tags: lv+=1
        if t=='relation' and 'building' in tags: rel_b+=1
        if t=='node' and 'building' in tags: bt['(node) '+tags['building']]+=1
        el.clear()
    elif t=='bounds': print('bounds',el.attrib)
print(dict(n)); print('ways highway:',sum(hw.values())); print(hw.most_common(25))
print('edificações (ways):',sum(v for k,v in bt.items() if not k.startswith('(node)')),' com nº de andares:',lv,' relações building:',rel_b)
print(bt.most_common(15))
