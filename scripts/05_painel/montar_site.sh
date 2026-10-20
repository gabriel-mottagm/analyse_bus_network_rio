#!/usr/bin/env bash
# Monta a versão do painel para o GitHub Pages em _site/ (ou na pasta indicada).
# painel/index.html é o fragmento publicado como Artifact no Claude (sem <!doctype>/<head>);
# aqui ele ganha o cabeçalho de um documento HTML completo.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
D="${1:-$RAIZ/_site}"
rm -rf "$D"; mkdir -p "$D/data"
{
  cat <<'EOF'
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Mapa e indicadores das 494 linhas de ônibus do Rio de Janeiro: tempo de espera, ônibus por dia, velocidade, horário e moradores atendidos a pé (GTFS SMTR, Censo 2022, OpenStreetMap).">
<meta property="og:title" content="Raio-X dos Ônibus do Rio">
<meta property="og:description" content="Mapa e indicadores das 494 linhas de ônibus do Rio de Janeiro.">
<meta property="og:image" content="og.png">
<style>body{margin:0;font:14px system-ui}[hidden]{display:none!important}</style>
EOF
  grep -v 'name="claude:' "$RAIZ/painel/index.html"
} > "$D/index.html"
cp "$RAIZ"/painel/data/linhas.json "$RAIZ"/painel/data/contexto.json "$D/data/"
cp "$RAIZ/docs/imagens/painel.png" "$D/og.png"
touch "$D/.nojekyll"
echo "Site montado em $D"
