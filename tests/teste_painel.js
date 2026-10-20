const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(async()=>chromium.launch());
  const out=process.argv[2];
  for (const [name,vp,scheme] of [['desk_light',{width:1440,height:900},'light'],['desk_dark',{width:1440,height:900},'dark'],['mobile',{width:390,height:844},'light']]){
    const ctx=await b.newContext({viewport:vp,colorScheme:scheme,deviceScaleFactor:1});
    const p=await ctx.newPage(); const errs=[];
    p.on('console',m=>{if(m.type()==='error')errs.push(m.text())}); p.on('pageerror',e=>errs.push(String(e)));
    await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
    await p.screenshot({path:`${out}/${name}_1.png`,fullPage:name==='mobile'});
    if(name==='desk_light'){
      await p.click('#ind-viagens'); await p.waitForTimeout(300); await p.screenshot({path:`${out}/${name}_2_viagens.png`});
      await p.click('#ind-espera'); await p.fill('#busca','474'); await p.waitForTimeout(300); await p.press('#busca','Enter'); await p.waitForTimeout(800);
      await p.screenshot({path:`${out}/${name}_3_ficha.png`});
      const box=await p.locator('#map').boundingBox(); await p.mouse.move(box.x+box.width*0.55,box.y+box.height*0.5); await p.waitForTimeout(300);
    }
    if(name==='desk_dark'){ await p.click('#ind-pop'); await p.waitForTimeout(300); await p.screenshot({path:`${out}/${name}_2_pop.png`}); }
    const ov=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
    console.log(name,'erros:',JSON.stringify(errs),'overflow-x:',ov);
    await ctx.close();
  }
  await b.close();
})();
