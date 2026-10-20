# Intermediário dos ônibus ao vivo (Cloudflare Worker)

A API de geolocalização da frota da SMTR (`https://its.mobilidade.rio/v1/geolocalizacao/veiculos`, beta, CC BY 4.0) não envia cabeçalhos CORS. Por isso o painel no GitHub Pages não consegue chamá-la direto do navegador. O `worker.js` resolve isso:
- busca as posições de **uma linha** (`?servico=474`) nos dois últimos minutos;
- devolve só a última posição de cada ônibus, num JSON enxuto, com CORS liberado para `https://gabriel-mottagm.github.io` e `localhost`;
- guarda a resposta por 30 s, de modo que todos os visitantes compartilham a mesma consulta. Isso respeita o limite de 5 pedidos/s da API.

## Publicar

1. Cloudflare → **Workers & Pages** → **Create** → **Create Worker** → nome `rio-onibus-aovivo` → **Deploy**.
2. **Edit code** → cole o conteúdo de `worker.js` → **Deploy**.
3. Teste: `https://rio-onibus-aovivo.<sua-conta>.workers.dev/?servico=474`.
4. Ponha o endereço em `AOVIVO_URL`, no início da seção "Ônibus ao vivo" de `painel/index.html`. Sem endereço, o recurso fica desligado.

O plano gratuito permite 100 mil pedidos por dia. Cada visitante com a ficha de uma linha aberta faz 2 pedidos por minuto.

## Resposta

```json
{"servico":"474","gerado":"2026-10-20T15:50:12Z","minutos":["2026-10-20T15:50:00Z","2026-10-20T15:49:00Z"],"n":10,
 "veiculos":[{"id":"A41234","lat":-22.97,"lon":-43.18,"vel":23,"dir":250,"sentido":"ida","rota":"O0474AAA0A","t":"2026-10-20T15:49:41Z"}],
 "fonte":"SMTR / Prefeitura do Rio – API de geolocalização da frota (beta), CC BY 4.0"}
```
