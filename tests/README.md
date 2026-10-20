# Testes do painel

Scripts Playwright (Node) usados durante o desenvolvimento para conferir o painel em computador e celular, temas claro e escuro, modo técnico, filtros e CSV.

Eles esperam:
- o painel servido em `http://localhost:8765/` (alguns abrem `_teste.html`, uma cópia de `painel/index.html`);
- o Playwright instalado (os scripts apontam para `/opt/npm-tools/node_modules/playwright`; troque por `require('playwright')`).

Exemplo:

```bash
cd painel && cp index.html _teste.html && python3 -m http.server 8765 &
node tests/teste_tec2.js
```

`window.claude` é simulado nos testes para o botão "Baixar CSV".

`teste_fundo.js` confere o mapa de fundo com o site montado por `scripts/05_painel/montar_site.sh` e servido em `http://localhost:8790/`. Ele troca o estilo do OpenFreeMap por um estilo de teste com as paradas em lon/lat do GTFS e compara a posição de cada parada no canvas e no MapLibre. O resultado esperado é um erro de cerca de 0,1 px. Também testa o fundo próprio quando o OpenFreeMap está inacessível.
