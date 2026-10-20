### Extrato OSM recebido (19/10/2026): avaliação

Arquivo BBBike `planet_-43_799_-23_089_-43_089_-22_739_osm.gz` (75 MB): 3,36 mi de nós, 543 mil ways, 141 mil trechos de via e 337 mil edificações. Ruas e edificações vêm no mesmo arquivo.

- **Rede de ruas: boa cobertura.** Só 2,3% da população mora em setores sem nenhum nó de via a pé. As favelas estão bem mapeadas (Complexo do Alemão: 34 nós/ha; Maré: 8,8; Rocinha: 14,6). Atenção: excluir também `highway=busway` (1.270 trechos, corredores de BRT).
- **Edificações: cobertura muito irregular.** 51% da população mora em setores sem nenhuma edificação mapeada (AP3 63%, AP5 59%, AP4 52%, AP2 14%). A Maré tem 181 de 241 setores sem edificação e a Cidade de Deus 51 de 60. Campo Grande é a exceção (0,66 edificação por domicílio). Usar as edificações do OSM para distribuir a população distorceria justamente as áreas pobres.
- **Decisão sugerida:** distribuir a população de cada setor ao longo das vias residenciais e de pedestres (ponderada pelo comprimento), com distribuição uniforme quando o setor não tiver via. A mesma rede serve para calcular a distância a pé.
- **Fontes alternativas de edificações**, se necessário: Overture Maps (combina OSM com footprints de aprendizado de máquina da Microsoft e do Google; CLI `pip install overturemaps` e `overturemaps download --bbox=-43.80,-23.09,-43.09,-22.74 -f geojson --type=building -o rio_edificacoes.geojson`, arquivo grande; conferir formatos com `overturemaps download --help`) ou IPP/Prefeitura (aplicativo ArcGIS, só áreas pequenas e servidor instável).
