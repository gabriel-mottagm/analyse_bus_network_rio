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
