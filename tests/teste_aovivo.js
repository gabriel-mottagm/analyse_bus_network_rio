// Testa a camada "ônibus ao vivo" com o Worker simulado.
// Pré-requisito: site montado em /tmp/site com AOVIVO_URL='https://teste-aovivo.example' e servido em http://localhost:8790/.
// Uso: node tests/teste_aovivo.js /tmp/mock_aovivo.json /tmp/teste_estilo.json [pasta_prints]
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/npm-tools/node_modules/playwright');
const fs = require('fs');
const [mockF, estiloF, OUT = '/tmp'] = process.argv.slice(2);
const mock = JSON.parse(fs.readFileSync(mockF, 'utf8'));
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const erros = [];
  const nova = async (vp, modoApi) => {
    const ctx = await b.newContext({ viewport: vp }); const p = await ctx.newPage(); p.on('pageerror', e => erros.push(String(e)));
    await p.route('https://tiles.openfreemap.org/**', r => r.fulfill({ contentType: 'application/json', body: fs.readFileSync(estiloF, 'utf8') }));
    const pedidos = [];
    await p.route('https://teste-aovivo.example/**', r => {
      pedidos.push(r.request().url());
      if (modoApi.falhar) return r.fulfill({ status: 502, contentType: 'application/json', body: '{"erro":"x"}' });
      const agora = Date.now();
      const veiculos = mock.vs.map(v => ({ ...v, t: new Date(agora - v.idade * 1000).toISOString() }));
      r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ servico: '474', n: veiculos.length, veiculos }) });
    });
    return { ctx, p, pedidos };
  };
  // 1) desktop: abre a 474, confere contagem, posição e hover
  let { ctx, p, pedidos } = await nova({ width: 1440, height: 900 }, {});
  await p.goto('http://localhost:8790/?teste'); await p.waitForFunction(() => window.__rxo && __rxo.BASE.ok, null, { timeout: 20000 });
  await p.fill('#busca', '474'); await p.waitForTimeout(300); await p.locator('#list .row').first().click();
  await p.waitForFunction(() => __rxo.AO.dados, null, { timeout: 10000 }); await p.waitForTimeout(1500);
  console.log('pedido:', pedidos[0]);
  console.log('ficha:', (await p.locator('#aoVivo').innerText()).replace(/\n+/g, ' / '));
  const r = await p.evaluate(raw => {
    const R = window.__rxo, m = R.BASE.map; let max = 0;
    const vs = R.AO.dados.vs; const ids = vs.map(v => v.id).sort().join(',');
    vs.forEach(v => { const o = raw.find(x => x.id === v.id); const q = m.project([o.lon, o.lat]); max = Math.max(max, Math.hypot(q.x - (v.x * R.T.k + R.T.x), q.y - (-v.y * R.T.k + R.T.y))) });
    return { ids, maxErroPx: +max.toFixed(2) };
  }, mock.vs);
  console.log('veículos no mapa:', r.ids, '| erro de posição máx.', r.maxErroPx, 'px');
  // hover num ônibus
  const alvo = await p.evaluate(() => { const R = window.__rxo, v = R.AO.dados.vs[0], c = document.getElementById('map').getBoundingClientRect(); return { x: c.left + v.x * R.T.k + R.T.x, y: c.top - v.y * R.T.k + R.T.y } });
  await p.mouse.move(alvo.x, alvo.y); await p.waitForTimeout(400);
  console.log('tooltip:', (await p.locator('#tip').innerText()).replace(/\n+/g, ' / '), '| visível', await p.locator('#tip').isVisible());
  await p.locator('#mapbox').screenshot({ path: `${OUT}/aovivo_mapa.png` });
  await p.locator('#aoVivo').screenshot({ path: `${OUT}/aovivo_ficha.png` });
  // troca de dia na ficha mantém a seção; voltar para a lista para de buscar
  await p.click('#diaSeg button:has-text("Sábado")'); await p.waitForTimeout(500);
  console.log('após trocar o dia, seção visível:', await p.locator('#aoVivo').isVisible());
  await p.click('#backBtn'); await p.waitForTimeout(300); const n0 = pedidos.length;
  console.log('voltou à lista: AO.linha =', await p.evaluate(() => __rxo.AO.linha), '| timer =', await p.evaluate(() => __rxo.AO.timer));
  await p.waitForTimeout(31000); console.log('pedidos depois de 31 s fora da ficha:', pedidos.length - n0);
  await ctx.close();
  // 2) falha do Worker
  ({ ctx, p } = await nova({ width: 1440, height: 900 }, { falhar: true }));
  await p.goto('http://localhost:8790/?teste'); await p.waitForTimeout(1500);
  await p.fill('#busca', '474'); await p.waitForTimeout(300); await p.locator('#list .row').first().click(); await p.waitForTimeout(1500);
  console.log('falha:', (await p.locator('#aoVivo').innerText()).replace(/\n+/g, ' / '));
  await ctx.close();
  // 3) celular
  ({ ctx, p } = await nova({ width: 390, height: 844 }, {}));
  await p.goto('http://localhost:8790/?teste'); await p.waitForFunction(() => window.__rxo && __rxo.BASE.ok, null, { timeout: 20000 });
  await p.fill('#busca', '474'); await p.waitForTimeout(300); await p.locator('#list .row').first().click();
  await p.waitForFunction(() => __rxo.AO.dados, null, { timeout: 10000 }); await p.waitForTimeout(1500);
  console.log('celular: largura', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.locator('#aoVivo').scrollIntoViewIfNeeded(); await p.screenshot({ path: `${OUT}/aovivo_celular.png` });
  await ctx.close();
  console.log('erros', JSON.stringify(erros)); await b.close();
})();
