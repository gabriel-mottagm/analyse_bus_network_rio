# Plano do painel — referência busmadrid.org

Atualizado em 19/10/2026.

## Tabelas derivadas já geradas (a partir do gtfs.zip)

Script: `expandir_gtfs.py` (pandas). Todas as tabelas são de serviço **programado**.

| Tabela | Grão | Linhas | Uso |
|---|---|---|---|
| partidas_expandidas.csv | 1 partida (linha × dia-tipo × sentido × horário) | 104.014 | oferta por hora, intervalos, amplitude, velocidade, veículo-km |
| resumo_paradas.csv | 1 parada | 7.493 | passagens/dia por dia-tipo, nº de linhas, intervalo médio no pico da manhã |
| passagens_parada_hora.csv | parada × dia-tipo × hora | ~5,4 mi de passagens agregadas | perfil horário por parada, mapas de calor |

Observações: frequencies com `exact_times=0` → horários de partida nominais (início da janela + n × intervalo). 86 viagens com horário fixo (sem frequencies) entram uma vez cada. Horas ≥ 24 foram normalizadas em `hora_do_dia` (0–23), mas a hora GTFS original foi mantida.

## Fase 1: indicadores por linha (feito em 19/10/2026)

Arquivo principal: `indicadores_linhas.csv` (494 linhas × 37 colunas) + `linhas_intervalo_por_faixa.csv` (linha × tipo de dia × faixa horária, formato longo) + `dicionario_indicadores_linhas.csv`. Scripts: `ind_oferta.py` → `ind_tracado.py` → `ind_pop_linha.py` → `ind_monta.py`.

Indicadores (todos de serviço programado):
- Oferta: partidas/dia (útil, sábado, domingo); intervalo médio por faixa horária no dia útil (madrugada 0–5h, pico manhã 6–9h, entrepico 9–16h, pico tarde 16–19h, noite 19–24h) e no dia todo de sábado/domingo, pelo método do busmadrid (por sentido, 60 × horas com partida ÷ partidas; média dos sentidos); primeira/última partida; amplitude de serviço; veículo-km/dia; frota mínima estimada no pico (Σ sentidos de partidas/h × duração em h, sem tempo de terminal).
- Traçado: extensão, velocidade comercial programada (extensão do traçado mais usado ÷ duração mediana), tortuosidade (vazia nas 41 circulares), divergência ida/volta (tolerância de 40 m; vazia nas 53 de um sentido).
- Território: população a 400 m e a 800 m a pé, população por partida, % da população atendida nos 30% de renda mais baixa e nos 30% de renda mais alta, % de pretos e pardos, renda média da área atendida; tarifa.

Achados:
- Intervalo no pico da manhã (dia útil): mediana de 16,5 min; 79 linhas não operam no pico (noturnas SN, executivas etc.). Menores intervalos: BRT 22 (1,8 min), BRT 61 e linha 232 (2,7 min).
- Velocidade programada: mediana de 23 km/h (ônibus), 29 km/h (BRT); de 11 km/h (851, 859) a 50 km/h (614, via Linha Amarela).
- Frota mínima estimada no pico: ~4,1 mil veículos no total (Internorte 1.229, Santa Cruz 922, Transcarioca 898, MOBI-Rio 542, Intersul 475).
- Divergência ida/volta média de 38% (muitos binários de mão única).
- As linhas atendem áreas de renda mais alta que a média: em média 19% da população atendida está nos 30% de renda mais baixa e 42% nos 30% de renda mais alta (referência neutra: 30%/30%). Entre as linhas comuns, o quartil que atende as áreas de renda mais baixa tem intervalo mediano no pico de 20 min, contra 13 min no quartil mais rico (correlação de Spearman fraca, −0,17).
- BRT: mediana de 16 mil pessoas a 400 m a pé e 73 mil a 800 m (estações espaçadas; 800 m é a referência usual).

## Fase 2: cobertura populacional — VERSÃO ATUAL: distância a pé (19/10/2026)

**Esta é a versão de referência.** A versão em linha reta (seção seguinte) fica só para comparação.

Fontes: GTFS SMTR; camada data.rio "Censo Demográfico 2022 – Setores" (13.782 setores, 6.211.223 hab.); OpenStreetMap (extrato BBBike, OSM XML gzip, 75 MB).

Método (scripts `rede_caminhada.py` → `pop_vias.py` → `dist_a_pe.py` → `agrega_a_pe.py` → `mapas_a_pe.py`; só numpy/scipy/pandas/matplotlib):
- Rede de caminhada não-direcionada: 19,8 mil km de vias; exclui motorway, busway, vias em obra/projeto, foot=no e áreas; trunk (ex.: Av. Brasil) mantida. 95% dos nós no componente principal (2º componente = Niterói, fora da análise; Paquetá isolada e sem ônibus).
- População de cada setor distribuída em pontos a cada ~20 m nas vias residenciais e de pedestres a até ~30 m do setor, ponderada pelo comprimento (sem calçadas e travessias mapeadas à parte, trunk, alças, ciclovias, túneis e pontes). Só 36 setores (0,2% da população) sem via próxima ficaram com distribuição uniforme. Edificações do OSM não foram usadas (cobertura irregular, ver abaixo).
- Paradas ligadas ao nó mais próximo (mediana de 14 m); Dijkstra multi-origem.
- Ônibus/h no pico = partidas de dia útil 6h–9h ÷ 3, somando as linhas com parada a até 400 m a pé, no sentido mais frequente de cada uma.

Resultados:

| Raio | % pop. a pé | % pop. em linha reta (mesma distribuição) | % com estação de BRT a pé |
|---|---|---|---|
| 200 m | 37,2% | 57,5% | 0,9% |
| 300 m | 54,4% | 75,2% | 2,1% |
| 400 m | **68,0%** | 85,8% | 3,8% |
| 500 m | 78,3% | 91,7% | 5,9% |
| 800 m | 93,0% | 98,0% | 13,3% |
| 1000 m | 96,7% | 99,1% | 18,1% |

- Fator de desvio (distância a pé ÷ linha reta até a parada mais próxima, para quem está a mais de 100 m): mediana 1,44; 30% abaixo de 1,3; 14% acima de 2,0. Entre paradas vizinhas em Copacabana, 1,16–1,50 (consistente com traçado em grade); os valores altos vêm de morros, condomínios fechados, lagoas e vias expressas.
- Nível de serviço a 400 m a pé no pico: 32,0% sem parada; 3,9% com menos de 4 ônibus/h; 9,1% com 4 a 10; 21,2% com 10 a 30; 33,8% com 30 ou mais.
- Por AP (% a 400 m a pé): AP1 68,3% · AP2 82,4% · AP3 71,7% · AP4 59,1% · AP5 62,2%. Na AP1 a queda vem dos morros (Santo Cristo 34%, Estácio 37%, Gamboa 54%, Santa Teresa 68%); Centro 99,7%, Lapa 100%.
- Renda: decil 1 = 40,9% a 400 m a pé (68,1% em linha reta), distância média de 519 m; decil 9 = 85,1%, 235 m; decil 10 = 72,0% (Barra e condomínios).
- Cor/raça: 72,9% dos brancos contra 64,0–64,4% dos pretos e pardos a 400 m a pé; com 10+ ônibus/h, 61,5% contra 49–50%.
- Renda × oferta (tercis): têm pouca oferta (sem parada a 400 m a pé ou <10 ônibus/h) 64% dos 30% de renda mais baixa, 43% do meio e 28% dos 30% de renda mais alta.
- **Área prioritária: 1,19 milhão de pessoas** nos 30% de renda mais baixa com pouca oferta (eram 752 mil em linha reta). Bairros: Santa Cruz 113 mil, Maré 87 mil (70% do bairro; 82 mil sem parada a 400 m a pé), Bangu 52 mil, Jacarepaguá 52 mil, Senador Camará 48 mil, Guaratiba 45 mil, Campo Grande 43 mil, Paciência 42 mil, Complexo do Alemão 34 mil (63% do bairro), Inhoaíba 26 mil.
- População por linha cai em média 39% em relação à linha reta (de 20% a 82%).

Saídas: cobertura_rede_a_pe, nivel_servico_a_pe, ap/ra/bairros_cobertura_a_pe, setores_cobertura_a_pe (com as duas versões), linhas_populacao_a_pe, paradas_populacao_a_pe, equidade_renda_a_pe, equidade_cor_raca_a_pe, prioridade_bairros_a_pe (CSV); mapas mapa_a_pe_1_nivel_servico, mapa_a_pe_2_renda_x_oferta, mapa_a_pe_3_prioridade, mapa_a_pe_4_desvio (PNG).

Ressalvas: sem relevo (ladeiras e escadarias contam só pela distância); travessias de vias expressas dependem das passarelas mapeadas no OSM; estações de BRT no canteiro central ligadas a um único nó; vans, trem, metrô, VLT e barcas fora da conta; Gericinó concentra o complexo penitenciário.

### Avaliação do extrato OSM

- 3,36 mi de nós, 543 mil ways, 141 mil trechos de via, 337 mil edificações.
- Ruas: boa cobertura; só 2,3% da população em setores sem nenhum nó de via a pé; favelas bem mapeadas (Complexo do Alemão 34 nós/ha, Maré 8,8, Rocinha 14,6).
- Edificações: 51% da população em setores sem nenhuma edificação mapeada (AP3 63%, AP5 59%, AP4 52%, AP2 14%); por isso não foram usadas. Alternativas, se um dia for preciso: Overture Maps (CLI `overturemaps`) ou IPP/Prefeitura (ArcGIS, áreas pequenas). O usuário decidiu não usar edificações completas.

## Versão anterior: linha reta + distribuição uniforme (só para comparação)

Método: população uniforme no setor em grade de 20 m (`raster.py` → `cobertura.py` → `mapa.py` / `mapas_renda.py`).
- 400 m: 85,3% (300 m 74,6%; 500 m 91,3%; 800 m 97,9%); BRT a 400 m 8,6%.
- Nível de serviço: 14,7% sem parada; 74% com 10+ ônibus/h.
- Decil 1 de renda: 65% a 400 m; decil 9: 95%.
- Área prioritária: 752 mil pessoas (41% dos 30% de renda mais baixa).
- Mapas: mapa_nivel_servico.png, mapa_1_renda.png, mapa_2_renda_x_oferta.png, mapa_3_prioridade.png.

## Como o OSM foi obtido

- BBBike extract com o recorte do Rio já preenchido, formato OSM XML gzip, enviado por e-mail: https://extract.bbbike.org/?sw_lng=-43.80&sw_lat=-23.09&ne_lng=-43.09&ne_lat=-22.74&format=osm.gz&city=Rio_de_Janeiro
- Testados e descartados: Geofabrik (só o Sudeste, 821 MB) e Overpass API (406 no principal, espelhos falhando).
- Formatos legíveis no ambiente do Claude sem bibliotecas extras: OSM XML, GraphML, GeoJSON, GeoPackage. PBF e GeoParquet não.

## O que o busmadrid.org faz

Mapa (MapLibre + CARTO/OSM) com as linhas coloridas pelo indicador escolhido, tabela ordenável, ficha por linha, filtros por faixa de valor, seletores de tipo de dia, faixa horária e ano, download em CSV e página de metodologia. A unidade de análise é a **linha**.

| Indicador Madrid | Fonte em Madrid | No Rio |
|---|---|---|
| Intervalo médio na faixa horária | GTFS | **Feito** |
| Expedições/dia | GTFS | **Feito** |
| Amplitude de serviço (última − primeira saída) | GTFS | **Feito** |
| Velocidade comercial programada | GTFS | **Feito** |
| Extensão (km) | GTFS shapes | **Feito** |
| Tortuosidade (extensão ÷ linha reta) | GTFS shapes | **Feito** |
| Divergência ida/volta (%) | GTFS shapes | **Feito** |
| Frota (pico) | dados da EMT | **Estimada** com o GTFS (limite inferior); a frota real exigiria GPS |
| População servida (raio a pé) | população por seção censitária + OSM | **Feito** a pé pela rede OSM (400 m e 800 m) + perfil de renda e cor/raça |
| Viajeros/dia, Δ interanual, viajeros/expedição | demanda aberta da EMT | Não há fonte aberta confirmada de demanda por linha no Rio |

## Dados necessários além do GTFS

1. ~~Censo 2022 por setor~~ (recebido: camada data.rio).
2. ~~OpenStreetMap (Rio)~~ (recebido: extrato BBBike).
3. Opcional: GPS dos ônibus (programado × realizado, frota real) e bilhetagem (demanda), caso a SMTR disponibilize; GTFS de trem/metrô/VLT/barcas para a rede integrada.

Ressalva: o ambiente do Claude não acessa o FTP do IBGE, o OSM nem o PyPI diretamente; arquivos externos precisam ser anexados.

## Proposta de fases

- **Fase 1, só GTFS**: tabela de indicadores por linha feita; falta o painel (mapa das linhas coloridas pelo indicador, filtros de dia/faixa, ficha da linha).
- **Fase 2, território**: feita com distância a pé; falta integrar ao painel.
- **Próximo passo**: painel interativo (mapa das linhas + tabela + ficha + camadas de cobertura) publicado como página web.
- **Fase 3, realizado** (se houver dados): GPS → cumprimento de viagens, velocidade real e frota real.
