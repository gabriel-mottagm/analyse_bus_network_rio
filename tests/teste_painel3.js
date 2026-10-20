const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const out=process.argv[2]; const errs=[];
  let ctx=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark',isMobile:true,hasTouch:true,deviceScaleFactor:2});
  let p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.evaluate(()=>document.querySelector('#mapbox').scrollIntoView()); await p.waitForTimeout(300); await p.screenshot({path:`${out}/m2_map.png`});
  await p.fill('#busca','474'); await p.press('#busca','Enter'); await p.waitForTimeout(1200); await p.screenshot({path:`${out}/m2_sel.png`});
  await ctx.close();
  ctx=await b.newContext({viewport:{width:1280,height:800},colorScheme:'light'}); p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.click('#dia-2'); await p.click('#ind-horas'); await p.waitForTimeout(300); await p.screenshot({path:`${out}/d2_horas.png`});
  await p.click('#modo-brt'); await p.click('#ind-espera'); await p.selectOption('#faixaSel','4'); await p.waitForTimeout(300);
  const box=await p.locator('#map').boundingBox(); for(let i=0;i<4;i++){await p.mouse.wheel(0,-300); await p.waitForTimeout(80)}
  await p.mouse.move(box.x+box.width*0.45,box.y+box.height*0.55); await p.waitForTimeout(200); await p.screenshot({path:`${out}/d2_brt_zoom.png`});
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
