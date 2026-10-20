const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async()=>{
  const b=await chromium.launch(); const out=process.argv[2]; const errs=[];
  const ctx=await b.newContext({viewport:{width:1280,height:800}}); const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/_teste.html'); await p.waitForTimeout(2500);
  const box=await p.locator('#map').boundingBox();
  await p.mouse.move(box.x+box.width*0.6,box.y+box.height*0.5);
  for(let i=0;i<5;i++){await p.mouse.wheel(0,-250); await p.waitForTimeout(60)}
  let found=null;
  for(let gy=0.2;gy<0.9&&!found;gy+=0.04) for(let gx=0.2;gx<0.9;gx+=0.03){await p.mouse.move(box.x+box.width*gx,box.y+box.height*gy); if(await p.locator('#tip').isVisible()){found=[gx,gy];break}}
  console.log('tooltip em',found, found? await p.locator('#tip').innerText():'');
  await p.screenshot({path:`${out}/d3_hover.png`});
  if(found){await p.mouse.click(box.x+box.width*found[0],box.y+box.height*found[1]); await p.waitForTimeout(500); console.log('ficha aberta:',await p.locator('#fichaView').isVisible(), (await p.locator('.sign').innerText()).replace(/\n/g,' '))}
  // drag
  await p.mouse.move(box.x+200,box.y+200); await p.mouse.down(); await p.mouse.move(box.x+350,box.y+260,{steps:5}); await p.mouse.up(); await p.waitForTimeout(200);
  await p.screenshot({path:`${out}/d3_drag.png`});
  console.log('erros',JSON.stringify(errs)); await b.close();
})();
