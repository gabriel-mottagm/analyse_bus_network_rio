// Testa o seletor de fundo do mapa (Claro / Escuro / Simples) no site servido em http://localhost:8790/.
// Os estilos do OpenFreeMap são trocados por estilos de teste (fundo verde-claro = Positron, cinza-escuro = Dark).
// Uso: node tests/teste_seletor_fundo.js [pasta_prints]
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/npm-tools/node_modules/playwright');
const OUT = process.argv[2] || '/tmp';
const URL = 'http://localhost:8790/?teste';
const estilo = cor => JSON.stringify({ version: 8, sources: {}, layers: [{ id: 'bg', type: 'background', paint: { 'background-color': cor } }] });
const rotear = async (p, pedidos, falhar) => p.route('https://tiles.openfreemap.org/**', r => {
  pedidos.push(r.request().url());
  if (falhar) return r.abort();
  r.fulfill({ contentType: 'application/json', body: estilo(r.request().url().includes('dark') ? '#2a2a2a' : '#dff0df') });
});
const estado = p => p.evaluate(() => ({
  ativo: [...document.querySelectorAll('#fundoSel button')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.textContent).join(),
  desab: [...document.querySelectorAll('#fundoSel button')].filter(b => b.disabled).map(b => b.textContent).join(),
  visivel: !document.getElementById('fundoSel').hidden,
  dataFundo: document.getElementById('mapbox').dataset.fundo,
  ok: __rxo.BASE.ok, mapa: !!__rxo.BASE.map, tema: __rxo.BASE.tema,
  basemapVisivel: getComputedStyle(document.getElementById('basemap')).display !== 'none',
  g1: getComputedStyle(document.getElementById('mapbox')).getPropertyValue('--g1').trim(),
  legenda1: document.querySelector('#legend .sw') && getComputedStyle(document.querySelector('#legend .sw')).backgroundColor,
  credito: document.getElementById('attrib').innerText,
  salvo: localStorage.getItem('rxo-fundo')
}));
const clicar = async (p, t) => { await p.click(`#fundoSel button:has-text("${t}")`); await p.waitForTimeout(1500) };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const erros = [];
  const nova = async (opts, falhar) => {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, ...opts }); const p = await ctx.newPage();
    p.on('pageerror', e => erros.push(String(e))); const pedidos = []; await rotear(p, pedidos, falhar); return { ctx, p, pedidos };
  };
  // 1) sistema claro, sem escolha salva
  let { ctx, p, pedidos } = await nova({ colorScheme: 'light' });
  await p.goto(URL); await p.waitForFunction(() => window.__rxo && __rxo.BASE.ok, null, { timeout: 20000 });
  console.log('1 inicial (claro)    ', JSON.stringify(await estado(p)));
  await clicar(p, 'Escuro'); await p.waitForFunction(() => __rxo.BASE.tema === 'escuro');
  console.log('2 escolhe Escuro     ', JSON.stringify(await estado(p)), '| estilos pedidos:', pedidos.map(u => u.split('/').pop()).join(','));
  await p.screenshot({ path: `${OUT}/seletor_escuro_pagina_clara.png` });
  await clicar(p, 'Simples');
  console.log('3 escolhe Simples    ', JSON.stringify(await estado(p)));
  await p.screenshot({ path: `${OUT}/seletor_simples.png` });
  // 4) recarrega: a escolha fica guardada e o MapLibre nem é carregado
  pedidos.length = 0; await p.reload(); await p.waitForTimeout(2500);
  console.log('4 recarregado        ', JSON.stringify(await estado(p)), '| pedidos de estilo:', pedidos.length);
  await clicar(p, 'Claro'); await p.waitForFunction(() => __rxo.BASE.ok, null, { timeout: 20000 });
  console.log('5 volta para Claro   ', JSON.stringify(await estado(p)));
  await p.screenshot({ path: `${OUT}/seletor_claro.png` });
  await ctx.close();
  // 6) sistema escuro, sem escolha salva
  ({ ctx, p } = await nova({ colorScheme: 'dark' }));
  await p.goto(URL); await p.waitForFunction(() => window.__rxo && __rxo.BASE.ok, null, { timeout: 20000 });
  console.log('6 inicial (escuro)   ', JSON.stringify(await estado(p)));
  await clicar(p, 'Claro'); await p.waitForFunction(() => __rxo.BASE.tema === 'claro');
  console.log('7 Claro c/ pág escura', JSON.stringify(await estado(p)));
  await p.screenshot({ path: `${OUT}/seletor_claro_pagina_escura.png` });
  await ctx.close();
  // 8) fundo externo inacessível
  ({ ctx, p } = await nova({ colorScheme: 'light' }, true));
  await p.goto(URL); await p.waitForTimeout(14000);
  console.log('8 sem OpenFreeMap    ', JSON.stringify(await estado(p)));
  await ctx.close();
  // 9) celular
  ({ ctx, p } = await nova({ viewport: { width: 390, height: 844 }, colorScheme: 'light' }));
  await p.goto(URL); await p.waitForFunction(() => window.__rxo && __rxo.BASE.ok, null, { timeout: 20000 });
  const caixas = await p.evaluate(() => ['fundoSel', 'attrib', 'legend'].map(id => { const r = document.getElementById(id).getBoundingClientRect(); return [id, Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] }));
  console.log('9 celular (l,t,r,b)  ', JSON.stringify(caixas), '| largura', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.locator('#mapbox').screenshot({ path: `${OUT}/seletor_celular.png` });
  await ctx.close();
  console.log('erros', JSON.stringify(erros)); await b.close();
})();
