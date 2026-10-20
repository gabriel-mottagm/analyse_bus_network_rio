const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const errs=[];
  const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
  // estado antigo salvo apontando para um indicador removido (índice 13) e coluna removida
  await p.addInitScript(()=>{try{localStorage.setItem('rxo-estado',JSON.stringify({ind:13,dia:0,faixa:1,modo:'Todas'}));localStorage.setItem('rxo-tec',JSON.stringify({tec:true,cols:['espera','pob','ren']}))}catch(e){}
    window.claude={use:async n=>n==='downloads'?{save:async o=>{window.__csv=o;return {status:'saved'}}}:null}});
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  console.log('chips técnicos:', (await p.locator('#tecChips .chip').allInnerTexts()).join(' | '));
  console.log('indicador ativo:', await p.locator('#tecHead h2').innerText());
  console.log('colunas:', (await p.locator('#tblBox thead th').allInnerTexts()).join(' | '));
  await p.click('#csvBtn'); await p.waitForTimeout(300); const o=await p.evaluate(()=>window.__csv); console.log('csv colunas:', o.data.split('\n')[0].split(',').length);
  await p.locator('#tblBox tbody tr').first().click(); await p.waitForTimeout(500); console.log('ficha técnica:', (await p.locator('.tecsec').innerText()).replace(/\n/g,' / '));
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
