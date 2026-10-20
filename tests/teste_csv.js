const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();
  await p.addInitScript(()=>{window.claude={use:async n=>n==='downloads'?{save:async o=>{window.__csv=o;return {status:'saved'}}}:null}});
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.click('#tecBtn'); await p.waitForTimeout(400); await p.click('#csvBtn'); await p.waitForTimeout(400);
  console.log('msg:', await p.locator('#tmsg').innerText());
  const o=await p.evaluate(()=>window.__csv); const L=o.data.split('\n');
  console.log('arquivo:',o.filename,'| linhas:',L.length-1,'| colunas:',L[0].split(',').length);
  console.log(L[0].replace('﻿','')); console.log(L.find(x=>x.startsWith('474,')));
  await b.close();
})();
