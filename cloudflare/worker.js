// Raio-X dos Ônibus do Rio: intermediário da API de geolocalização da SMTR
// ---------------------------------------------------------------------------
// A API https://its.mobilidade.rio/v1/geolocalizacao/veiculos (beta, CC BY 4.0, SMTR/PCRJ) não envia
// cabeçalhos CORS, então o painel no GitHub Pages não pode chamá-la direto do navegador.
// Este Worker busca as posições de UMA linha, guarda a resposta por 30 s (todos os visitantes
// compartilham a mesma consulta, o que respeita o limite de 5 pedidos/s da API) e devolve
// só a última posição de cada ônibus, num JSON enxuto, com CORS liberado para o painel.
//
// Uso:  GET https://<seu-worker>.workers.dev/?servico=474
// Resposta: { servico, gerado, minutos, n, veiculos:[{id, lat, lon, vel, dir, sentido, rota, t}], fonte }

const API = 'https://its.mobilidade.rio/v1/geolocalizacao/veiculos';
const ORIGENS = ['https://gabriel-mottagm.github.io'];       // sites que podem usar este Worker
const CACHE_S = 30;                                            // segundos de cache por linha
const MEM = new Map();   // cache em memória da instância (o Cache API pode não funcionar em *.workers.dev)
const FONTE = 'SMTR / Prefeitura do Rio – API de geolocalização da frota (beta), CC BY 4.0';

export default {
  async fetch(req, env, ctx) {
    const origem = req.headers.get('Origin') || '';
    const permitida = ORIGENS.includes(origem) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origem);
    const cors = {
      'Access-Control-Allow-Origin': permitida ? origem : ORIGENS[0],
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Vary': 'Origin',
    };
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (req.method !== 'GET') return json({ erro: 'Use GET.' }, 405, cors);

    const url = new URL(req.url);
    const servico = (url.searchParams.get('servico') || '').trim();
    if (!/^[A-Za-z0-9]{1,12}$/.test(servico)) return json({ erro: 'Informe a linha: ?servico=474' }, 400, cors);

    const m = MEM.get(servico);
    if (m && Date.now() - m.em < CACHE_S * 1000) return comCors(new Response(m.corpo, { headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': `public, max-age=${CACHE_S}` } }), cors, 'HIT-MEM');
    const cache = typeof caches !== 'undefined' ? caches.default : null;
    const chave = new Request(`https://cache.raio-x-onibus/v1?servico=${encodeURIComponent(servico)}`);
    if (cache) {
      const c = await cache.match(chave);
      if (c) return comCors(c, cors, 'HIT');
    }

    try {
      // o minuto atual ainda está chegando; junta com o anterior e fica com a posição mais recente de cada ônibus
      const agora = Date.now();
      const minutos = [0, 1].map(a => { const d = new Date(agora - a * 60000); d.setUTCSeconds(0, 0); return d.toISOString().replace('.000', ''); });
      const listas = await Promise.all(minutos.map(m => buscar(servico, m)));
      const ultimo = new Map();
      for (const v of listas.flat()) {
        if (v.latitude == null || v.longitude == null || !v.id_veiculo) continue;
        const t = Date.parse(v.datetime || v.datetime_servidor || '') || 0;
        const atual = ultimo.get(v.id_veiculo);
        if (!atual || t > atual._t) ultimo.set(v.id_veiculo, { ...v, _t: t });
      }
      const veiculos = [...ultimo.values()].sort((a, b) => a.id_veiculo < b.id_veiculo ? -1 : 1).map(v => ({
        id: v.id_veiculo, lat: +v.latitude, lon: +v.longitude,
        vel: v.velocidade == null ? null : +v.velocidade, dir: v.direcao == null ? null : +v.direcao,
        sentido: v.sentido || null, rota: v.route_id || null, t: v.datetime || v.datetime_servidor || null,
      }));
      const corpo = { servico, gerado: new Date(agora).toISOString(), minutos, n: veiculos.length, veiculos, fonte: FONTE };
      const texto = JSON.stringify(corpo);
      MEM.set(servico, { em: agora, corpo: texto }); if (MEM.size > 600) MEM.delete(MEM.keys().next().value);
      const resp = new Response(texto, {
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': `public, max-age=${CACHE_S}` },
      });
      if (cache) ctx.waitUntil(cache.put(chave, resp.clone()));
      return comCors(resp, cors, 'MISS');
    } catch (e) {
      return json({ erro: 'A API da SMTR não respondeu agora.', detalhe: String(e && e.message || e) }, 502, cors);
    }
  },
};

async function buscar(servico, minuto) {
  const todos = []; let cursor = null;
  for (let pagina = 0; pagina < 5; pagina++) {
    const u = new URL(API);
    u.searchParams.set('servico', servico); u.searchParams.set('minuto_utc', minuto); u.searchParams.set('limit', '1000');
    if (cursor) u.searchParams.set('cursor', cursor);
    const r = await fetch(u.toString(), { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(20000) });
    if (!r.ok) throw new Error(`API respondeu ${r.status}`);
    const j = await r.json();
    if (Array.isArray(j.data)) todos.push(...j.data);
    cursor = j.next_cursor;
    if (!cursor) break;
  }
  return todos;
}

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...cors } });
}
function comCors(resp, cors, cacheStatus) {
  const r = new Response(resp.body, resp);
  for (const [k, v] of Object.entries(cors)) r.headers.set(k, v);
  r.headers.set('X-Cache', cacheStatus);
  return r;
}
