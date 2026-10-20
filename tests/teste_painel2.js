const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const out=process.argv[2];
  let ctx=await b.newContext({viewport:{width:390,height:844},colorScheme:'light',isMobile:true,hasTouch:true,deviceScaleFactor:2});
  let p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.screenshot({path:`${out}/m_top.png`});
  const h=await p.evaluate(()=>document.documentElement.scrollHeight); console.log('altura pagina mobile',h);
  await p.evaluate(()=>document.querySelector('#panel').scrollIntoView()); await p.waitForTimeout(300); await p.screenshot({path:`${out}/m_list.png`});
  await p.locator('.row').first().click(); await p.waitForTimeout(800); await p.screenshot({path:`${out}/m_ficha_map.png`});
  await p.evaluate(()=>document.querySelector('#fichaView').scrollIntoView()); await p.waitForTimeout(300); await p.screenshot({path:`${out}/m_ficha.png`});
  console.log('erros',JSON.stringify(errs)); await ctx.close();
  ctx=await b.newContext({viewport:{width:1440,height:900},colorScheme:'light'}); p=await ctx.newPage(); await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.screenshot({path:`${out}/d_espera.png`});
  await p.click('#aboutBtn'); await p.waitForTimeout(300); await p.screenshot({path:`${out}/d_sobre.png`});
  await b.close();
})();
