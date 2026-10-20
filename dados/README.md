# Insumos

O pipeline usa três insumos. Só o GTFS está no repositório; os outros dois são grandes e públicos.

| Insumo | Onde fica no repositório | Para onde vai na pasta de trabalho | Como obter |
|---|---|---|---|
| GTFS da SMTR (ônibus e BRT, gerado em 03/06/2026, válido até 31/12/2026) | `dados/gtfs_smtr_2026-06.zip` (25 MB) | `trabalho/gtfs/` (descompactado) | `unzip dados/gtfs_smtr_2026-06.zip -d trabalho/gtfs`. Versões novas são publicadas pela SMTR / data.rio |
| Censo 2022 por setor censitário (13.782 setores, 6.211.223 hab.) | não incluído (37 MB) | `trabalho/censo/setores.geojson` | Camada "Censo Demográfico 2022 – Setores" no data.rio, exportada em GeoJSON. O campo `valor_do_r` é a renda; `SHAPE__Area` está em Web Mercator |
| OpenStreetMap, recorte do Rio | não incluído (75 MB) | `trabalho/osm/rio.osm.gz` | BBBike extract, formato "OSM XML gzip'd" (chega por e-mail): https://extract.bbbike.org/?sw_lng=-43.80&sw_lat=-23.09&ne_lng=-43.09&ne_lat=-22.74&format=osm.gz&city=Rio_de_Janeiro |

Observações:
- O extrato OSM usado foi baixado em 19/10/2026. Um extrato mais novo dá resultados ligeiramente diferentes.
- A Overpass API (consultas em `scripts/diagnosticos/*.overpassql`) é uma alternativa ao BBBike, mas o script espera OSM XML.
- Se quiser versionar os insumos grandes, use Git LFS.
