// Testa o mapa de fundo (MapLibre) do painel servido em http://localhost:8790/ (scripts/05_painel/montar_site.sh).
// 1) Alinhamento: o estilo do OpenFreeMap é trocado por um estilo de teste com paradas e traçados em lon/lat crus do GTFS;
//    compara a posição na tela de cada parada no canvas (dados projetados) e no MapLibre (map.project).
// 2) Sem fundo: com o OpenFreeMap inacessível, o painel continua com o fundo próprio e sem erros.
// Uso: node tests/teste_fundo.js /tmp/teste_estilo.json /tmp/raw_stops.json [pasta_prints]
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/npm-tools/node_modules/playwright');
const fs = require('fs');
const [estiloF, paradasF, OUT = '/tmp'] = process.argv.slice(2);
const URL = 'http://localhost:8790/?teste';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const raw = JSON.parse(fs.readFileSync(paradasF, 'utf8'));
  const erros = [];
  // ---------- 1) alinhamento ----------
  for (const [vp, esquema] of [[{ width: 1440, height: 900 }, 'light'], [{ width: 390, height: 844 }, 'dark']]) {
    const ctx = await b.newContext({ viewport: vp, colorScheme: esquema });
    const p = await ctx.newPage(); p.on('pageerror', e => erros.push(String(e)));
    await p.route('https://tiles.openfreemap.org/**', r => r.fulfill({ contentType: 'application/json', body: fs.readFileSync(estiloF, 'utf8') }));
    await p.goto(URL); await p.waitForFunction(() => window.__rxo && window.__rxo.BASE.ok, null, { timeout: 20000 });
    const medir = async rot => {
      const r = await p.evaluate(raw => {
        const R = window.__rxo, T = R.T, m = R.BASE.map, W = R.W, H = R.H; let max = 0, soma = 0, n = 0;
        R.D.paradas.forEach((s, i) => {
          const cx = s[0] * T.k + T.x, cy = -s[1] * T.k + T.y; if (cx < 0 || cy < 0 || cx > W || cy > H) return;
          const q = m.project(raw[i]); const d = Math.hypot(q.x - cx, q.y - cy); max = Math.max(max, d); soma += d; n++;
        });
        return { n, max: +max.toFixed(2), media: +(soma / Math.max(1, n)).toFixed(2), zoom: +m.getZoom().toFixed(2) };
      }, raw);
      console.log(`${vp.width}px ${esquema} ${rot}: ${r.n} paradas na tela, erro médio ${r.media} px, máximo ${r.max} px (zoom ${r.zoom})`);
      return r;
    };
    await p.waitForTimeout(800); await medir('cidade');
    await p.screenshot({ path: `${OUT}/fundo_${vp.width}_${esquema}_cidade.png` });
    // aproxima no Centro e em Campo Grande
    for (const [rot, n, f] of [['zoom 1', 4, 1.6], ['zoom 2', 4, 1.6]]) {
      for (let i = 0; i < n; i++) await p.click('#zin');
      await p.waitForTimeout(600); await medir(rot);
    }
    // arrasta
    const box = await p.locator('#map').boundingBox();
    await p.mouse.move(box.x + box.width / 2, box.y + box.height / 2); await p.mouse.down();
    await p.mouse.move(box.x + box.width / 2 + 180, box.y + box.height / 2 + 90, { steps: 8 }); await p.mouse.up();
    await p.waitForTimeout(500); await medir('depois de arrastar');
    // linha selecionada: 474
    await p.fill('input[placeholder^="Número"]', '474'); await p.waitForTimeout(400);
    await p.locator('#list .row').first().click(); await p.waitForTimeout(2500); await medir('linha 474');
    await p.screenshot({ path: `${OUT}/fundo_${vp.width}_${esquema}_474.png` });
    console.log('  crédito:', await p.locator('#attrib').innerText());
    await ctx.close();
  }
  // ---------- 2) sem fundo ----------
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage(); p.on('pageerror', e => erros.push(String(e)));
  await p.route('https://tiles.openfreemap.org/**', r => r.abort());
  await p.goto(URL); await p.waitForTimeout(1500);
  console.log('sem fundo, 1,5 s: ok=', await p.evaluate(() => window.__rxo.BASE.ok), '| linhas na lista', await p.locator('#list .row').count());
  await p.screenshot({ path: `${OUT}/fundo_sem_1s.png` });
  await p.waitForTimeout(12000);
  console.log('sem fundo, 13 s: mapa removido=', await p.evaluate(() => window.__rxo.BASE.map === null), '| crédito:', await p.locator('#attrib').innerText());
  await p.screenshot({ path: `${OUT}/fundo_sem_13s.png` });
  await ctx.close();
  console.log('erros', JSON.stringify(erros)); await b.close();
})();
