#!/usr/bin/env bash
# Roda o pipeline completo: GTFS + Censo 2022 + OSM → indicadores, mapas e dados do painel.
#
# Uso:  ./pipeline.sh [pasta_de_trabalho]        (padrão: ./trabalho)
#
# A pasta de trabalho precisa ter, antes de rodar (ver dados/README.md):
#   gtfs/                  GTFS descompactado (unzip dados/gtfs_smtr_2026-06.zip -d trabalho/gtfs)
#   censo/setores.geojson  setores do Censo 2022 (data.rio)
#   osm/rio.osm.gz         extrato OSM XML gzip do Rio (BBBike)
#
# Tempo total: ~15–25 min e ~6 GB de memória (a etapa da caminhada é a mais pesada).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")" && pwd)"
S="$RAIZ/scripts"
T="${1:-$RAIZ/trabalho}"
PY="${PYTHON:-python3}"
cd "$T"
for f in gtfs/stops.txt censo/setores.geojson osm/rio.osm.gz; do
  [ -e "$f" ] || { echo "Falta $T/$f (ver dados/README.md)"; exit 1; }
done
mkdir -p out cob ape linhas painel/data
etapa(){ echo; echo "== $*"; }

etapa "1. GTFS: expandir frequências em partidas"
$PY "$S/01_gtfs/expandir_gtfs.py" gtfs out

etapa "2. Censo: rasterizar setores (grade de 20 m) e cobertura em linha reta (comparação)"
$PY "$S/02_linha_reta/raster.py" censo/setores.geojson censo
$PY "$S/02_linha_reta/cobertura.py" gtfs censo cob out
$PY "$S/02_linha_reta/mapa.py" censo cob
$PY "$S/02_linha_reta/mapas_renda.py" censo cob

etapa "3. Distância a pé pela rede do OSM (versão de referência)"
$PY "$S/03_a_pe/rede_caminhada.py" osm/rio.osm.gz censo osm
$PY "$S/03_a_pe/pop_vias.py" censo osm
$PY "$S/03_a_pe/dist_a_pe.py" gtfs censo osm cob ape out
$PY "$S/03_a_pe/agrega_a_pe.py" censo osm cob ape
$PY "$S/03_a_pe/mapas_a_pe.py" censo osm ape

etapa "4. Indicadores por linha"
$PY "$S/04_indicadores/ind_oferta.py" out linhas
$PY "$S/04_indicadores/ind_tracado.py" gtfs out linhas
$PY "$S/04_indicadores/ind_pop_linha.py" gtfs censo osm ape linhas
$PY "$S/04_indicadores/ind_monta.py" gtfs ape linhas
$PY "$S/04_indicadores/ind_pontos_parada.py" gtfs linhas

etapa "5. Dados do painel"
$PY "$S/05_painel/painel_contexto.py" censo osm/rio.osm.gz painel/data
$PY "$S/05_painel/painel_linhas.py" gtfs out linhas painel/data

echo; echo "Pronto. Para atualizar o painel do repositório: cp $T/painel/data/*.json $RAIZ/painel/data/"
