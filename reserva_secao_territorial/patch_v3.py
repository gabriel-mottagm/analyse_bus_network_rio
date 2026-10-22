import sys
p=sys.argv[1]; s=open(p).read()
def R(a,b,count=1):
    global s
    assert s.count(a)==count, ('anchor',a[:80],s.count(a))
    s=s.replace(a,b)

# ---------- CSS: tokens das camadas ----------
R("  --n1:#d5cff5; --n2:#ada2ec; --n3:#8676df; --n4:#6250d6; --n5:#46379f; --n6:#2c2268;\n  --font-ui:",
  "  --n1:#d5cff5; --n2:#ada2ec; --n3:#8676df; --n4:#6250d6; --n5:#46379f; --n6:#2c2268;\n"
  "  --c0:#e5683c; --c1:#9ec5f4; --c2:#5598e7; --c3:#256abf; --c4:#0d366b; --res:#cfcbc1; --pri:#c0392b;\n"
  "  --d1:#c9d9e8; --d2:#f6c79e; --d3:#e5683c; --d4:#a8401a;\n"
  "  --v00:#d6d6d6; --v01:#e4acac; --v02:#c85a5a; --v10:#b0d5df; --v11:#ad9ea5; --v12:#985356; --v20:#64acbe; --v21:#627f8c; --v22:#574249;\n"
  "  --font-ui:")
dark_add=("  --c0:#e8784f; --c1:#1f3f66; --c2:#2f6fc4; --c3:#5598e7; --c4:#a9cdf6; --res:#3a3b36; --pri:#ef6a5c;\n"
          "  --d1:#33475c; --d2:#8a5a35; --d3:#d0603a; --d4:#f0a58a;\n")
R("  --n1:#3a2f86; --n2:#4f40b0; --n3:#6a59d6; --n4:#8b7de6; --n5:#ab9fef; --n6:#cbc3f6;\n  color-scheme:dark}",
  "  --n1:#3a2f86; --n2:#4f40b0; --n3:#6a59d6; --n4:#8b7de6; --n5:#ab9fef; --n6:#cbc3f6;\n"+dark_add+"  color-scheme:dark}",count=2)
R("/* Sobre */",
"""/* Abas e bairros */
.tabs{display:flex;border-bottom:1px solid var(--rule)}
.tab{flex:1;padding:10px 8px 9px;border:0;border-bottom:2px solid transparent;background:none;cursor:pointer;font-weight:600;color:var(--muted)}
.tab[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--accent)}
.bbar{display:flex;height:8px;border-radius:4px;overflow:hidden;width:68px;background:var(--surface-2)}
.bbar i{display:block;height:100%}
.nvbar{display:flex;height:16px;border-radius:5px;overflow:hidden;width:100%}
.nvbar i{display:block;height:100%}
.nvleg{display:grid;grid-template-columns:1fr auto;gap:2px 10px;font-size:13px;margin-top:8px}
.nvleg span:nth-child(even){text-align:right;font-variant-numeric:tabular-nums}
.nvleg b{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.lns{display:flex;flex-wrap:wrap;gap:6px}
.lns button{border:0;padding:0;background:none;cursor:pointer}
.lns .pill{font-size:14px;min-width:40px}
.metsel{border:1px solid var(--rule);background:var(--surface);border-radius:8px;padding:3px 8px;font-size:13px;max-width:100%}
.bivleg{display:grid;grid-template-columns:auto repeat(3,26px);gap:2px;align-items:center;font-size:11px;color:var(--muted)}
.bivleg i{display:block;height:18px;border-radius:2px}
.bivwrap{display:flex;gap:10px;align-items:flex-end}
.bivnotes{font-size:12px;color:var(--ink-2);display:grid;gap:4px}
.tip .bn{display:block;font-weight:600}

/* Sobre */""")

# ---------- HTML: seletor de camada e abas ----------
R('    <div class="ctl search grow"',
  '    <div class="ctl">\n      <label class="lbl" for="camSel">Camada no mapa</label>\n      <select class="sel" id="camSel"></select>\n    </div>\n    <div class="ctl search grow"')
R('<aside class="panel" id="panel">',
  '<aside class="panel" id="panel">\n    <div class="tabs" role="tablist"><button class="tab" id="tabLinhas" role="tab" type="button">Linhas</button><button class="tab" id="tabBairros" role="tab" type="button">Bairros</button></div>')
R('    <div id="fichaView" class="ficha" hidden></div>',
  '    <div id="fichaView" class="ficha" hidden></div>\n'
  '    <div id="bListView" style="display:none;flex-direction:column;min-height:0;flex:1">\n'
  '      <div class="phead"><h2 id="bTitle">Bairros</h2><div class="meta" id="bMeta"></div>\n'
  '        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><label class="meta" for="bMet">Ordenar por</label><select class="metsel" id="bMet"></select><button class="sortbtn" id="bSort" type="button"></button></div></div>\n'
  '      <div class="list" id="bList" role="list"></div>\n'
  '    </div>\n'
  '    <div id="bFichaView" class="ficha" hidden></div>')

# ---------- JS: estado e carga ----------
R("const S={ind:0,dia:0,faixa:1,modo:'Todas',busca:'',sel:null,hover:null,sortGood:true,view:'list',lim:40,",
  "const S={ind:0,dia:0,faixa:1,modo:'Todas',busca:'',sel:null,hover:null,sortGood:true,view:'list',lim:40,tab:'linhas',cam:0,bsel:null,bhover:null,bmet:0,bdesc:true,")
R("Promise.all([fetch('data/linhas.json').then(r=>r.json()),fetch('data/contexto.json').then(r=>r.json())]).then(([d,c])=>{D=d;CTX=c;init()})",
  "const loadImg=src=>new Promise((ok,err)=>{const im=new Image();im.onload=()=>ok(im);im.onerror=err;im.src=src});\n"
  "let TER=null;\n"
  "Promise.all([fetch('data/linhas.json').then(r=>r.json()),fetch('data/contexto.json').then(r=>r.json()),fetch('data/territorio.json').then(r=>r.json()),loadImg('data/camadas_a.png'),loadImg('data/camadas_b.png')]).then(([d,c,t,ia,ib])=>{D=d;CTX=c;TER=t;decodeLayers(ia,ib);init()})")

# ---------- controles ----------
R("    b.addEventListener('click',()=>{S.ind=i;update()});chips.appendChild(b)});",
  "    b.addEventListener('click',()=>{S.ind=i;if(S.cam&&S.tab==='linhas')S.cam=0;update()});chips.appendChild(b)});\n"
  "  const cs=$('#camSel');CAMS.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.nome;cs.appendChild(o)});\n"
  "  cs.addEventListener('change',()=>{S.cam=+cs.value;update()});\n"
  "  $('#tabLinhas').addEventListener('click',()=>setTab('linhas'));\n"
  "  $('#tabBairros').addEventListener('click',()=>setTab('bairros'));\n"
  "  const bm=$('#bMet');BMET.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.nome;bm.appendChild(o)});\n"
  "  bm.addEventListener('change',()=>{S.bmet=+bm.value;S.bdesc=BMET[S.bmet].desc;renderBList()});\n"
  "  $('#bSort').addEventListener('click',()=>{S.bdesc=!S.bdesc;renderBList()});")
R("  $('#busca').addEventListener('input',e=>{S.busca=norm(e.target.value.trim());S.lim=40;renderList()});",
  "  $('#busca').addEventListener('input',e=>{S.busca=norm(e.target.value.trim());S.lim=40;renderList();renderBList()});")
R("  $('#busca').addEventListener('keydown',e=>{if(e.key==='Enter'){const f=visibleSorted()[0];if(f)select(f.id,true)}});",
  "  $('#busca').addEventListener('keydown',e=>{if(e.key==='Enter'){if(S.tab==='bairros'){const b=bSorted()[0];if(b!=null)selectB(b,true)}else{const f=visibleSorted()[0];if(f)select(f.id,true)}}});")
R("function syncControls(){",
  "function syncControls(){\n  $('#camSel').value=S.cam;\n  $('#tabLinhas').setAttribute('aria-selected',S.tab==='linhas'); $('#tabBairros').setAttribute('aria-selected',S.tab==='bairros');\n  $('#bMet').value=S.bmet;")

# ---------- views ----------
R("function showView(v){\n  S.view=v; $('#listView').hidden=v!=='list'; $('#fichaView').hidden=v!=='ficha'; $('#aboutView').hidden=v!=='about';\n  $('#listView').style.display=v==='list'?'flex':'none';",
  "function showView(v){\n  S.view=v; $('#listView').hidden=v!=='list'; $('#fichaView').hidden=v!=='ficha'; $('#aboutView').hidden=v!=='about';\n  $('#bFichaView').hidden=v!=='bficha';\n  $('#listView').style.display=v==='list'?'flex':'none'; $('#bListView').style.display=v==='blist'?'flex':'none';")
R("$('#aboutBtn').addEventListener('click',()=>showView(S.view==='about'?(S.sel!=null?'ficha':'list'):'about'));",
  "$('#aboutBtn').addEventListener('click',()=>showView(S.view==='about'?(S.tab==='bairros'?(S.bsel!=null?'bficha':'blist'):(S.sel!=null?'ficha':'list')):'about'));")
R("function select(id,fit){\n  S.sel=id;",
  "function select(id,fit){\n  if(S.tab!=='linhas'){S.tab='linhas';S.bsel=null;syncControls();}\n  S.sel=id;")

# ---------- legenda: camada ----------
R("function renderLegend(){\n",
  "function renderLegend(){\n  if(S.cam){renderLayerLegend();return}\n")

# ---------- render: camada, linhas em cinza, contorno de bairro ----------
R("  ctx.fillStyle=C['--map-city']; ctx.fill(ctxPaths.city,'evenodd');",
  "  ctx.fillStyle=C['--map-city']; ctx.fill(ctxPaths.city,'evenodd');\n"
  "  if(S.cam){const lc=layerCanvas(S.cam); const [gx0,gy0,AG,GX,GY]=TER.origem; ctx.imageSmoothingEnabled=false; ctx.drawImage(lc,gx0,-(gy0+GY*AG),GX*AG,GY*AG); ctx.imageSmoothingEnabled=true}")
R("  ctx.globalAlpha=dim?0.18:1;",
  "  ctx.globalAlpha=dim?0.18:1;\n"
  "  if(S.cam||S.tab==='bairros'){ctx.globalAlpha=dim?0.25:(S.cam?0.55:0.4); ctx.lineWidth=Math.max(1,lw*0.6)*px; ctx.strokeStyle=C['--ink']; ctx.globalAlpha*=0.5; [binPaths.nd,...binPaths.b].forEach(pp=>ctx.stroke(pp)); ctx.globalAlpha=1} else {")
R("  ctx.lineWidth=lw*px*0.8; ctx.strokeStyle=C['--nd']; ctx.stroke(binPaths.nd);",
  "  ctx.lineWidth=lw*px*0.8; ctx.strokeStyle=C['--nd']; ctx.stroke(binPaths.nd);")
R("  order.forEach(i=>{ctx.lineWidth=lw*px; ctx.strokeStyle=cssv(ind.pal[i]); ctx.stroke(binPaths.b[i])});\n  ctx.globalAlpha=1;",
  "  order.forEach(i=>{ctx.lineWidth=lw*px; ctx.strokeStyle=cssv(ind.pal[i]); ctx.stroke(binPaths.b[i])});\n  ctx.globalAlpha=1; }\n"
  "  const bo=(i,w,col)=>{if(i==null) return; const b=TER.bairros[i]; ctx.lineWidth=(w+3)*px; ctx.strokeStyle=C['--surface']; b._p=b._p||(()=>{const q=new Path2D(); b.g.forEach(g=>q.addPath(toPath(g,true))); return q})(); ctx.stroke(b._p); ctx.lineWidth=w*px; ctx.strokeStyle=col; ctx.stroke(b._p)};\n"
  "  if(S.tab==='bairros'){ if(S.bhover!=null&&S.bhover!==S.bsel) bo(S.bhover,1.5,C['--ink']); bo(S.bsel,2.5,C['--accent']); }")

# ---------- hover e clique ----------
R("  if(e.pointerType==='mouse'){const id=pick(mx,my);",
  "  if(e.pointerType==='mouse'&&S.tab==='bairros'){const bi=bairroAt(mx,my); if(bi!==S.bhover){S.bhover=bi; draw()} cv.classList.toggle('hovering',bi!=null); showBTip(bi,mx,my); return}\n"
  "  if(e.pointerType==='mouse'){const id=pick(mx,my); if(id==null&&S.cam){S.hover!=null&&(S.hover=null,draw()); cv.classList.remove('hovering'); showCellTip(mx,my); return}")
R("if(id!=null) select(id,false); else if(S.sel!=null) deselect()",
  "if(S.tab==='bairros'){const bi=bairroAt(e.clientX-r.left,e.clientY-r.top); if(bi!=null) selectB(bi,false); else if(S.bsel!=null) deselectB()} else if(id!=null) select(id,false); else if(S.sel!=null) deselect()")
R("const endPtr=e=>{const r=cv.getBoundingClientRect();",
  "const endPtr=e=>{const r=cv.getBoundingClientRect(); const id=(drag&&!moved&&e.type==='pointerup'&&S.tab!=='bairros')?pick(e.clientX-r.left,e.clientY-r.top):null;")
R("if(drag&&!moved&&e.type==='pointerup'){const id=pick(e.clientX-r.left,e.clientY-r.top); if(S.tab==='bairros')",
  "if(drag&&!moved&&e.type==='pointerup'){if(S.tab==='bairros')")

# ---------- ciclo ----------
R("function update(){\n  S.lim=40; syncControls(); buildBins(); renderLegend(); renderList();",
  "function update(){\n  S.lim=40; syncControls(); buildBins(); renderLegend(); renderList(); renderBList();\n  if(S.bsel!=null&&S.view==='bficha') renderBFicha(S.bsel);")
R("readColors(); renderLegend(); renderList(); draw()",
  "readColors(); layerCache={}; renderLegend(); renderList(); renderBList(); if(S.bsel!=null&&S.view==='bficha') renderBFicha(S.bsel); draw()")

# ---------- sobre ----------
R("  <h3>Mapa</h3>",
  "  <h3>Camadas do mapa e bairros</h3>\n"
  "  <ul>\n"
  "   <li><b>Ônibus perto de casa:</b> para cada quadra (quadrícula de 100 m), a classe da maioria dos moradores: sem parada a até 400 m de caminhada, ou quantos ônibus por hora passam a até 400 m no pico da manhã de dia útil (somando as linhas, no sentido mais frequente de cada uma).</li>\n"
  "   <li><b>Renda e ônibus:</b> cruza a renda média do responsável pelo domicílio (Censo 2022, em três faixas com o mesmo número de pessoas) com a oferta de ônibus a pé no pico.</li>\n"
  "   <li><b>Onde falta ônibus:</b> moradores dos 30% de setores de renda mais baixa que não têm parada a até 400 m a pé ou têm menos de 10 ônibus por hora no pico.</li>\n"
  "   <li><b>Caminho até o ponto:</b> quanto a caminhada pelas ruas até a parada mais próxima é mais longa que a linha reta. Valores altos indicam morros, vias expressas, linhas de trem e condomínios fechados.</li>\n"
  "   <li>A população de cada setor do Censo foi distribuída ao longo das ruas onde as pessoas moram. Os limites de bairro são aproximados. Gericinó concentra o complexo penitenciário, e Paquetá não tem linhas de ônibus.</li>\n"
  "  </ul>\n"
  "  <h3>Mapa</h3>")

# ---------- novos módulos ----------
NEW=r"""
/* ---------- Camadas territoriais ---------- */
const CAMS=[
 {nome:'Nenhuma (só as linhas)'},
 {nome:'Ônibus perto de casa',titulo:'Ônibus perto de casa',sub:'Ônibus por hora a até 400 m a pé · pico da manhã, dia útil',
  labels:['Sem parada a até 5 min a pé','Menos de 4 ônibus/h','4 a 10 ônibus/h','10 a 30 ônibus/h','30 ou mais ônibus/h'],tok:['--c0','--c1','--c2','--c3','--c4']},
 {nome:'Renda e ônibus',titulo:'Renda e ônibus no pico'},
 {nome:'Onde falta ônibus',titulo:'Onde falta ônibus'},
 {nome:'Caminho até o ponto',titulo:'Caminho até o ponto',sub:'Distância a pé ÷ linha reta até a parada mais próxima',
  labels:['Quase direto (menos de 1,3×)','1,3 a 1,6×','1,6 a 2×','2× ou mais (desvio grande)','Parada a menos de 100 m'],tok:['--d1','--d2','--d3','--d4','--res']},
];
const BIV=[['--v00','--v01','--v02'],['--v10','--v11','--v12'],['--v20','--v21','--v22']];
let LY=null, layerCache={};
function decodeLayers(ia,ib){
  const rd=im=>{const c=document.createElement('canvas'); c.width=im.width; c.height=im.height; const x=c.getContext('2d'); x.drawImage(im,0,0); return x.getImageData(0,0,im.width,im.height).data};
  const a=rd(ia), b=rd(ib), n=ia.width*ia.height;
  LY={w:ia.width,h:ia.height,niv:new Uint8Array(n),biv:new Uint8Array(n),pri:new Uint8Array(n),desv:new Uint8Array(n),dens:new Uint8Array(n),bai:new Uint8Array(n)};
  for(let i=0;i<n;i++){const j=i*4; LY.niv[i]=Math.round(a[j]/40); LY.biv[i]=Math.round(a[j+1]/25); LY.pri[i]=Math.round(a[j+2]/50);
    LY.desv[i]=Math.round(b[j]/40); LY.dens[i]=Math.round(b[j+1]/35); LY.bai[i]=b[j+2]}
}
const hexrgb=h=>{h=h.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]};
const DALPHA=[0,0.42,0.58,0.72,0.84,0.93,1];
function layerCanvas(cam){
  if(layerCache[cam]) return layerCache[cam];
  const c=document.createElement('canvas'); c.width=LY.w; c.height=LY.h; const x=c.getContext('2d'); const im=x.createImageData(LY.w,LY.h), d=im.data;
  const res=hexrgb(cssv('--res'));
  let col;
  if(cam===1){const t=CAMS[1].tok.map(k=>hexrgb(cssv(k))); col=i=>LY.niv[i]?t[LY.niv[i]-1]:null}
  else if(cam===2){const t=[]; for(let q=0;q<9;q++) t.push(hexrgb(cssv(BIV[Math.floor(q/3)][q%3]))); col=i=>LY.biv[i]?t[LY.biv[i]-1]:(LY.dens[i]?res:null)}
  else if(cam===3){const pr=hexrgb(cssv('--pri')); col=i=>LY.pri[i]?pr:(LY.dens[i]?res:null)}
  else {const t=CAMS[4].tok.map(k=>hexrgb(cssv(k))); col=i=>LY.desv[i]?t[LY.desv[i]-1]:null}
  for(let i=0;i<LY.niv.length;i++){const v=col(i); if(!v) continue; const j=i*4; d[j]=v[0]; d[j+1]=v[1]; d[j+2]=v[2];
    let a=DALPHA[LY.dens[i]]||0.4; if(cam===3&&LY.pri[i]) a=[0,0.45,0.65,0.85,1][LY.pri[i]]; if(cam===3&&!LY.pri[i]) a=0.55;
    d[j+3]=Math.round(a*255)}
  x.putImageData(im,0,0); layerCache[cam]=c; return c;
}
function cellAt(mx,my){
  const [gx0,gy0,AG,GX,GY]=TER.origem; const wx=(mx-T.x)/T.k, wy=-(my-T.y)/T.k;
  const cx=Math.floor((wx-gx0)/AG), cy=Math.floor((wy-gy0)/AG); if(cx<0||cy<0||cx>=GX||cy>=GY) return -1;
  return (GY-1-cy)*GX+cx;
}
function bairroAt(mx,my){const i=cellAt(mx,my); if(i<0) return null; const b=LY.bai[i]; return b?b-1:null}
function showCellTip(mx,my){
  const i=cellAt(mx,my); if(i<0||!LY.dens[i]){tip.hidden=true;return}
  let t='';
  if(S.cam===1) t=LY.niv[i]?CAMS[1].labels[LY.niv[i]-1]:'';
  else if(S.cam===2){const q=LY.biv[i]-1; if(q>=0){const y=Math.floor(q/3), x=q%3; t=`Renda ${['mais alta','média','mais baixa'][x]} · ${['muitos ônibus','oferta média','poucos ônibus'][y]}`}}
  else if(S.cam===3) t=LY.pri[i]?'Moradores de baixa renda com pouco ônibus':'Fora da área prioritária';
  else if(S.cam===4) t=LY.desv[i]?CAMS[4].labels[LY.desv[i]-1]:'';
  const b=LY.bai[i]?TER.bairros[LY.bai[i]-1].n:'';
  tip.innerHTML=`<span class="bn">${esc(b)}</span><span class="v">${esc(t)}</span>`; placeTip(mx,my);
}
function showBTip(bi,mx,my){
  if(bi==null){tip.hidden=true;return}
  const b=TER.bairros[bi]; const m=BMET[S.bmet];
  tip.innerHTML=`<span class="bn">${esc(b.n)}</span><span class="v">${m.show(b)}</span>`; placeTip(mx,my);
}
function placeTip(mx,my){tip.hidden=false; const r=tip.getBoundingClientRect(); let x=mx+14,y=my+14; if(x+r.width>W-6) x=mx-r.width-14; if(y+r.height>H-6) y=my-r.height-14; tip.style.left=Math.max(6,x)+'px'; tip.style.top=Math.max(6,y)+'px'}
function renderLayerLegend(){
  const c=CAMS[S.cam], L=TER.cidade, lg=$('#legend'); lg.classList.toggle('closed',!S.legOpen);
  let h=`<button class="lgt" id="lgToggle" type="button" aria-expanded="${S.legOpen}"><h3>${c.titulo}</h3><span class="car">${S.legOpen?'ocultar':'legenda'}</span></button>`;
  if(S.cam===1||S.cam===4){
    const pct=S.cam===1?L.leg_nivel:L.leg_desv;
    h+=`<div class="sub">${c.sub} · % dos moradores da cidade</div><ul>`;
    c.labels.forEach((t,i)=>{h+=`<li><span class="sw" style="background:${cssv(c.tok[i])};height:10px"></span><span>${t}</span><span class="ct num">${fmt(pct[i],0)}%</span></li>`});
    h+='</ul>';
  } else if(S.cam===2){
    const P=L.leg_biv; let g='<div class="bivleg"><span></span><span style="grid-column:span 3;text-align:center">renda →</span>';
    ['Poucos','Médio','Muitos'].forEach((r,y)=>{g+=`<span>${r}</span>`; [2,1,0].forEach(x=>{const q=(2-y)*3+x; g+=`<i style="background:${cssv(BIV[2-y][x])}" title="${fmt(P[q],0)}% dos moradores"></i>`})});
    g+='<span></span><span style="text-align:center">baixa</span><span style="text-align:center">média</span><span style="text-align:center">alta</span></div>';
    h+=`<div class="sub">Ônibus por hora a até 400 m a pé (pico) × renda do bairro</div><div class="bivwrap">${g}<div class="bivnotes"><span>Tons escuros: baixa renda e poucos ônibus.</span><span>Ônibus: poucos = sem parada ou menos de 10/h; muitos = 30 ou mais/h.</span></div></div>`;
  } else if(S.cam===3){
    h+=`<div class="sub">Pico da manhã, dia útil</div><ul><li><span class="sw" style="background:${cssv('--pri')};height:10px"></span><span>30% de renda mais baixa sem parada a 5 min a pé ou com menos de 10 ônibus/h</span><span class="ct num">${fmt(L.pri/1e6,2)} mi</span></li><li><span class="sw" style="background:${cssv('--res')};height:10px"></span><span>Demais moradores</span><span></span></li></ul><div class="note">Vermelho mais forte: mais gente nessa situação.</div>`;
  }
  h+=`<div class="note">Linhas de ônibus em cinza. Escolha "Nenhuma" para colorir as linhas.</div>`;
  lg.innerHTML=h;
  $('#lgToggle').addEventListener('click',()=>{S.legOpen=!S.legOpen; renderLegend(); if(!userView&&S.sel==null&&S.bsel==null){fitBox(CITYB);draw()}});
}

/* ---------- Bairros ---------- */
const pc=v=>v==null?'—':fmt(v,0)+'%';
const BMET=[
 {nome:'Parada a até 5 min a pé',get:b=>b.p4,show:b=>`${pc(b.p4)} dos moradores têm parada a até 5 min a pé`,short:b=>pc(b.p4),desc:false},
 {nome:'10 ou mais ônibus/h perto',get:b=>b.bom,show:b=>`${pc(b.bom)} têm 10 ou mais ônibus/h a até 5 min a pé no pico`,short:b=>pc(b.bom),desc:false},
 {nome:'Caminhada até o ponto',get:b=>b.dist,show:b=>`caminhada média de ${fmt(b.dist)} m até o ponto`,short:b=>`${fmt(b.dist)} m`,desc:true},
 {nome:'Pessoas onde falta ônibus',get:b=>b.pri,show:b=>`${fmt(b.pri)} moradores onde falta ônibus (${pc(b.ppri)})`,short:b=>b.pri>=1000?`${fmt(b.pri/1000)} mil`:fmt(b.pri),desc:true},
 {nome:'População',get:b=>b.pop,show:b=>`${fmt(b.pop)} moradores`,short:b=>b.pop>=1000?`${fmt(b.pop/1000)} mil`:fmt(b.pop),desc:true},
];
function setTab(t){
  if(S.tab===t) return; S.tab=t; S.hover=null; S.bhover=null; tip.hidden=true;
  if(t==='bairros'){ if(!S.cam) S.cam=1; showView(S.bsel!=null?'bficha':'blist'); }
  else { showView(S.sel!=null?'ficha':'list'); }
  update();
}
function bSorted(){
  const m=BMET[S.bmet];
  const arr=TER.bairros.map((b,i)=>i).filter(i=>!S.busca||norm(TER.bairros[i].n).includes(S.busca));
  arr.sort((a,b)=>{const va=m.get(TER.bairros[a]),vb=m.get(TER.bairros[b]); if(va==null) return 1; if(vb==null) return -1; return S.bdesc?vb-va:va-vb});
  return arr;
}
function nvBar(nv,cls='bbar'){const tok=CAMS[1].tok; return `<span class="${cls}">${nv.map((v,i)=>v>0?`<i style="width:${v}%;background:${cssv(tok[i])}"></i>`:'').join('')}</span>`}
function renderBList(){
  if(!TER) return; const m=BMET[S.bmet], arr=bSorted();
  $('#bTitle').textContent='Bairros';
  $('#bMeta').textContent=`${arr.length} bairro${arr.length===1?'':'s'}${S.busca?' encontrados':''} · barra: ônibus perto de casa, do vermelho (sem parada) ao azul-escuro`;
  $('#bSort').textContent=S.bdesc?'Maiores primeiro':'Menores primeiro';
  const frag=document.createDocumentFragment();
  arr.forEach(i=>{const b=TER.bairros[i]; const r=document.createElement('button'); r.type='button'; r.className='row'; r.setAttribute('role','listitem');
    r.innerHTML=`${nvBar(b.nv)}<span style="min-width:0"><span class="nm">${esc(b.n)}</span><span class="md">${esc(b.ra)} · ${esc(b.ap)} · ${fmt(b.pop)} hab.</span></span><span class="val num">${m.short(b)}</span>`;
    r.addEventListener('click',()=>selectB(i,true)); r.addEventListener('mouseenter',()=>{S.bhover=i;draw()}); r.addEventListener('mouseleave',()=>{S.bhover=null;draw()});
    frag.appendChild(r)});
  const L=$('#bList'); L.innerHTML=''; if(arr.length) L.appendChild(frag); else L.innerHTML='<div class="empty">Nenhum bairro com esse nome.</div>';
}
function selectB(i,fit){
  if(S.tab!=='bairros'){S.tab='bairros'; if(!S.cam) S.cam=1; syncControls(); renderLegend()}
  S.bsel=i; renderBFicha(i); showView('bficha'); const b=TER.bairros[i];
  if(fit&&b.bb){userView=true; fitBox(b.bb,0.12)} draw();
  if(window.matchMedia('(max-width:900px)').matches) $('#mapbox').scrollIntoView({behavior:'smooth',block:'start'});
}
function deselectB(){S.bsel=null; showView('blist'); draw()}
function renderBFicha(i){
  const b=TER.bairros[i], C_=TER.cidade, tok=CAMS[1].tok;
  let lead;
  if(!b.pop) lead='Bairro sem moradores no Censo 2022.';
  else lead=`<strong class="num">${pc(b.p4)}</strong> dos moradores têm uma parada de ônibus a até 5 minutos a pé. Na cidade, são ${pc(C_.p4)}.`;
  const nota=b.n==='Gericinó'?'<p class="foot">A população recenseada em Gericinó está quase toda no complexo penitenciário.</p>':(b.n==='Paquetá'?'<p class="foot">Paquetá não tem linhas de ônibus; o acesso é por barca.</p>':'');
  const ls=b.ln.map(id=>D.linhas[id]);
  $('#bFichaView').innerHTML=`
   <button class="back" id="bBack" type="button">← Todos os bairros</button>
   <div class="fhead">
     <h2 style="margin:0;font-family:var(--font-disp);font-size:28px;line-height:1.05">${esc(b.n)}</h2>
     <div class="tags"><span class="tag">${esc(b.ra)}</span><span class="tag">${esc(b.ap)}</span><span class="tag num">${fmt(b.pop)} moradores</span>${b.dens?`<span class="tag num">${fmt(b.dens)} hab/km²</span>`:''}</div>
     <p class="lead">${lead}</p>${nota}
   </div>
   <div class="sec"><h4>Ônibus perto de casa · pico da manhã</h4>${nvBar(b.nv,'nvbar')}
     <div class="nvleg">${CAMS[1].labels.map((t,k)=>`<span><b style="background:${cssv(tok[k])}"></b>${t}</span><span>${fmt(b.nv[k],0)}%</span>`).join('')}</div></div>
   <div class="facts">
     <div class="fact"><div class="k">Caminhada até o ponto</div><div class="v num">${fmt(b.dist)} m</div><div class="s">média do bairro · cidade: ${fmt(C_.dist)} m</div></div>
     <div class="fact"><div class="k">10 ou mais ônibus/h perto</div><div class="v num">${pc(b.bom)}</div><div class="s">dos moradores · cidade: ${pc(C_.bom)}</div></div>
     <div class="fact"><div class="k">Onde falta ônibus</div><div class="v num">${b.pri>=1000?fmt(b.pri/1000)+' mil':fmt(b.pri)}</div><div class="s">${pc(b.ppri)} do bairro: baixa renda e pouco ônibus</div></div>
     <div class="fact"><div class="k">Parada a até 10 min a pé</div><div class="v num">${pc(b.p8)}</div><div class="s">800 m de caminhada</div></div>
     <div class="fact"><div class="k">Renda média do responsável</div><div class="v num">${b.renda?'R$ '+fmt(b.renda):'—'}</div><div class="s">Censo 2022</div></div>
     <div class="fact"><div class="k">Desvio da caminhada</div><div class="v num">${b.desv?fmt(b.desv,1)+'×':'—'}</div><div class="s">a pé ÷ linha reta</div></div>
   </div>
   <div class="sec"><h4>Linhas que param no bairro · ${ls.length}</h4>${ls.length?`<div class="lns">${ls.map(l=>`<button type="button" data-id="${l.id}" title="${esc(l.nome)}"><span class="pill">${esc(l.n)}</span></button>`).join('')}</div><div class="foot" style="margin-top:6px">Das que mais rodam para as que menos rodam em dia útil. Toque para ver a linha.</div>`:'<p class="foot">Nenhuma linha de ônibus para neste bairro.</p>'}</div>`;
  $('#bBack').addEventListener('click',deselectB);
  $('#bFichaView').querySelectorAll('.lns button').forEach(x=>x.addEventListener('click',()=>{S.cam=0; select(+x.dataset.id,true); update()}));
}
"""
R("/* ---------- Ciclo ---------- */", NEW+"\n/* ---------- Ciclo ---------- */")
open(p,'w').write(s)
print('ok')
