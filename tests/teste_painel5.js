const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const errs=[];
  const p=await (await b.newContext({viewport:{width:1280,height:900}})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  console.log('chips:',(await p.locator('#indChips .chip').allInnerTexts()).join(' | '));
  await p.fill('#busca','474'); await p.press('#busca','Enter'); await p.waitForTimeout(800);
  await p.locator('.facts').scrollIntoViewIfNeeded(); await p.screenshot({path:process.argv[2]+'/ficha_ppar.png'});
  console.log((await p.locator('.facts').innerText()).replace(/\n/g,' / '));
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
