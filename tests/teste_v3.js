const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const out=process.argv[2]; const errs=[];
  for (const [nm,scheme] of [['L','light'],['D','dark']]){
    const p=await (await b.newContext({viewport:{width:1440,height:900},colorScheme:scheme})).newPage(); p.on('pageerror',e=>errs.push(nm+': '+e)); p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_TUNNEL'))errs.push(nm+' console: '+m.text())});
    await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
    for (const v of ['1','2','3','4']){ await p.selectOption('#camSel',v); await p.waitForTimeout(400); await p.screenshot({path:`${out}/v3_${nm}_cam${v}.png`}); }
    if(nm==='L'){
      await p.selectOption('#camSel','0'); await p.click('#tabBairros'); await p.waitForTimeout(400); await p.screenshot({path:`${out}/v3_L_bairros.png`});
      await p.selectOption('#bMet','3'); await p.waitForTimeout(200);
      await p.locator('#bList .row').first().click(); await p.waitForTimeout(800); await p.screenshot({path:`${out}/v3_L_bficha.png`});
      console.log('ficha bairro:', (await p.locator('#bFichaView h2').innerText()), '| fatos:', (await p.locator('#bFichaView .facts').innerText()).replace(/\n/g,' / '));
      const box=await p.locator('#map').boundingBox(); await p.mouse.move(box.x+box.width*0.5,box.y+box.height*0.5); await p.waitForTimeout(200);
      console.log('tip bairro:', await p.locator('#tip').isVisible()? (await p.locator('#tip').innerText()).replace(/\n/g,' | '):'(nenhuma)');
      await p.locator('#bFichaView .lns button').first().click(); await p.waitForTimeout(800); await p.screenshot({path:`${out}/v3_L_linha_do_bairro.png`});
      console.log('aba após clicar linha:', await p.locator('#tabLinhas').getAttribute('aria-selected'), 'camada:', await p.inputValue('#camSel'), 'ficha linha visível:', await p.locator('#fichaView').isVisible());
    }
  }
  const p=await (await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2})).newPage(); p.on('pageerror',e=>errs.push('M: '+e));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  await p.click('#tabBairros'); await p.waitForTimeout(400); await p.evaluate(()=>document.querySelector('#mapbox').scrollIntoView()); await p.waitForTimeout(300); await p.screenshot({path:`${out}/v3_M_bairros.png`});
  const ov=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth); console.log('mobile overflow-x',ov);
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
