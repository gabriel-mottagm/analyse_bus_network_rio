const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const out=process.argv[2]; const errs=[];
  const ctx=await b.newContext({viewport:{width:1440,height:900}}); await ctx.grantPermissions(['clipboard-read','clipboard-write']);
  const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_TUNNEL'))errs.push('console: '+m.text())});
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  console.log('geral: tecCtl oculto =',await p.locator('#tecCtl').isHidden(), '| chips:', (await p.locator('#indChips .chip').count()));
  await p.click('#tecBtn'); await p.waitForTimeout(600); await p.screenshot({path:`${out}/tec_1.png`});
  console.log('técnico: chips técnicos =',await p.locator('#tecChips .chip').count(), '| linhas na tabela =', await p.locator('#tblBox tbody tr').count());
  await p.click('#ind-frota'); await p.waitForTimeout(400); await p.screenshot({path:`${out}/tec_2_frota.png`});
  console.log('1ª linha frota (maior primeiro):', (await p.locator('#tblBox tbody tr').first().innerText()).replace(/\t|\n/g,' | '));
  // filtro: espera no pico entre 0 e 10 e % mais pobres >= 30
  await p.selectOption('#fK','espera'); await p.fill('#fMin','0'); await p.fill('#fMax','10'); await p.click('#fAdd'); await p.waitForTimeout(300);
  await p.selectOption('#fK','pob'); await p.fill('#fMin','30'); await p.click('#fAdd'); await p.waitForTimeout(400);
  console.log('após filtros:', await p.locator('#tecHead .meta').innerText(), '| chips filtro:', await p.locator('.fchip').count());
  await p.screenshot({path:`${out}/tec_3_filtros.png`});
  // ordenar por velocidade
  await p.locator('#tblBox th[data-k="vel"]').click(); await p.waitForTimeout(200);
  console.log('ordem vel:', await p.locator('#tblBox th[data-k="vel"]').getAttribute('aria-sort'));
  await p.click('#copyBtn'); await p.waitForTimeout(300); console.log('copiar:', await p.locator('#tmsg').innerText());
  const clip=await p.evaluate(()=>navigator.clipboard.readText()); console.log('clipboard 2 linhas:', clip.split('\n').slice(0,2).join(' || '));
  await p.click('#csvBtn'); await p.waitForTimeout(300); console.log('csv (fora do claude):', await p.locator('#tmsg').innerText());
  const csv=await p.evaluate(()=>{return null}); 
  await p.locator('#tblBox tbody tr').first().click(); await p.waitForTimeout(700); await p.locator('.tecsec').scrollIntoViewIfNeeded(); await p.screenshot({path:`${out}/tec_4_ficha.png`});
  console.log('ficha técnica:', (await p.locator('.tecsec').innerText()).replace(/\n/g,' / ').slice(0,300));
  await p.click('#tecBtn'); await p.waitForTimeout(500); console.log('voltou ao geral: lista visível =', await p.locator('#list').isVisible()||await p.locator('#fichaView').isVisible(), '| tecsec presente =', await p.locator('.tecsec').count());
  await p.click('#backBtn').catch(()=>{}); await p.waitForTimeout(300); console.log('lista geral linhas:', await p.locator('#list .row').count()); await p.screenshot({path:`${out}/tec_5_geral.png`});
  const m=await (await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2})).newPage(); m.on('pageerror',e=>errs.push('M '+e));
  await m.goto('http://localhost:8765/_teste.html'); await m.waitForTimeout(2500); await m.click('#tecBtn'); await m.waitForTimeout(500);
  await m.evaluate(()=>document.querySelector('#panel').scrollIntoView()); await m.waitForTimeout(300); await m.screenshot({path:`${out}/tec_m.png`});
  console.log('mobile overflow-x', await m.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth));
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
