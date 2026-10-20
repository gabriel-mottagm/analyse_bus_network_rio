# Perfil dos dados GTFS — ônibus do Rio de Janeiro

Arquivo analisado: `gtfs.zip` (arquivos gerados em 03/06/2026), publicado pela SMTR (Secretaria Municipal de Transportes). Análise feita em 19/10/2026.

## Visão geral

- **5 operadores**: os 4 consórcios do SPPO (Internorte, Intersul, Santa Cruz, Transcarioca) + MOBI-Rio (BRT).
- **494 linhas**: 436 ônibus regulares (route_type 700), 30 BRT (702), 28 executivos/frescões (200).
- **7.694 paradas** (7.490 pontos + 201 terminais/estações), cobrindo todo o município (Santa Cruz ao Centro).
- **961 traçados** (shapes) com 361 mil pontos.
- **3 tipos de dia**: útil (U_REG), sábado (S_REG), domingo/feriado (D_REG). Feriados de 2026 tratados em calendar_dates.
- **Validade**: feed_info vai de 01/01/2024 a 31/12/2026; calendar vai até 31/12/2027.
- **Feed baseado em frequência**: 17.275 das 17.361 viagens em trips.txt são *modelos* expandidos por frequencies.txt (janela + intervalo). Só 86 viagens (9 linhas) têm horário fixo.

## Tabelas

| Arquivo | Linhas | Grão | Chave |
|---|---|---|---|
| agency | 5 | operador | agency_id |
| routes | 494 | linha | route_id |
| trips | 17.361 | viagem-modelo (linha × dia × sentido × faixa horária) | trip_id |
| frequencies | 17.275 | janela de operação de uma viagem-modelo | trip_id (1:1) |
| stop_times | 1.031.419 | passagem de uma viagem-modelo por uma parada | trip_id + stop_sequence |
| stops | 7.694 | parada / estação | stop_id |
| shapes | 361.022 | ponto de traçado | shape_id + shape_pt_sequence |
| calendar / calendar_dates | 3 / 29 | tipo de dia / exceção (feriado) | service_id (+date) |
| fare_attributes / fare_rules | 13 / 489 | tarifa / tarifa por linha | fare_id / route_id |

Relações: agency → routes → trips → (frequencies, stop_times → stops); trips → shapes; trips → calendar; routes → fare_rules → fare_attributes. Integridade referencial: 100% íntegra (nenhuma chave órfã).

## Números derivados (programação, não operação real)

| Indicador | Dia útil | Sábado | Domingo/feriado |
|---|---|---|---|
| Partidas programadas | 50.310 | 31.183 | 22.521 |
| Veículo-km programados | ~1,18 milhão | ~742 mil | ~536 mil |
| Veículo-hora programadas | ~53 mil | ~31 mil | ~20 mil |
| Linhas em operação | 493 | 416 | 382 |

- Pico da manhã às 6h (4.163 partidas/h em dia útil); pico da tarde às 17h (3.411).
- Viagem típica: 58 paradas, 24 km, 63 min; velocidade comercial programada mediana de 22,5 km/h (p5 15 km/h, p95 35 km/h).
- Intervalo mediano no pico da manhã: 15 min por linha/sentido (25% das linhas ≤ 8 min).
- Linhas por parada: mediana 5; 1.107 paradas atendidas por uma única linha; maior concentração na Cidade Nova (BRS, 93 linhas) e Estação Barão de Mauá (91).
- Linhas com mais partidas em dia útil: BRT 22 (Alvorada–Jardim Oceânico, 886), BRT 60 (Deodoro–Gentileza, 607), SP864 (Campo Grande–Bangu, 572).
- Tarifas: R$ 5,00 (regular e BRT), executivos R$ 15,00 a R$ 24,85.

## Problemas de qualidade

| Gravidade | Problema |
|---|---|
| Alta | **Feed vence em 31/12/2026** (feed_info). Calendar vai até 2027, mas calendar_dates só tem 2 feriados de 2027. |
| Alta | Só há **serviço programado**: não há demanda, frota real, cumprimento de viagens nem tempo real. |
| Média | `timepoint` = 0 em 100% dos stop_times: todos os horários por parada são estimados/interpolados. |
| Média | `wheelchair_boarding` 100% vazio: não dá para medir acessibilidade. |
| Média | 5 linhas sem tarifa (LECD149, SN805, SN319, SN292, LECD150). |
| Baixa | fare_rules traz coluna `agency_id` fora do padrão GTFS, com códigos (SC, TC, IN, IS) que não batem com agency.txt. |
| Baixa | route_desc usado para códigos internos (LECD54, SVB685) misturados com "Expresso/Parador"; 73,7% vazio. |
| Baixa | 10 linhas sem cor; cor do texto mistura maiúsculas e minúsculas (FFFFFF / ffffff). |
| Baixa | IDs em dois formatos (stop_id de 12 caracteres vs 4; shape_id UUID vs 4 caracteres): parecem ser fontes distintas (SPPO vs BRT) combinadas. |
| Baixa | 3 paradas com location_type vazio; 3 nomes de parada com espaços sobrando; stop_code 93% vazio. |
| Info | Horários > 24:00 (ex.: 25:00) representam serviço madrugada adentro, como manda o padrão GTFS. |
| Info | 53 linhas com um só sentido (41 delas são circulares); 62 combinações linha/dia/sentido com mais de um traçado (variantes). |

## Ideias de indicadores para o painel

1. **Oferta ao longo do dia**: partidas/hora por linha, operador, região e tipo de dia.
2. **Intervalo (headway) por linha e período**: pico, entrepico, noite, madrugada; "quanto tempo espero no ponto".
3. **Velocidade comercial programada** por linha e trecho (dist/tempo entre paradas): onde o ônibus é lento.
4. **Cobertura espacial**: área a até 400–500 m de uma parada, cruzada com população do Censo IBGE por setor censitário.
5. **Conectividade de paradas**: nº de linhas e partidas por parada; mapa de calor de oferta.
6. **Acesso a oportunidades**: a partir de um ponto, até onde chego em 30/60 min (isócronas com r5/OpenTripPlanner).
7. **Ficha da linha**: traçado, extensão, tempo de viagem, paradas, intervalos, tarifa, operador.
8. **Comparação útil × sábado × domingo**: queda de oferta no fim de semana por região.

Complementos recomendados: GPS dos ônibus (para comparar programado × realizado), Censo IBGE (população), limites de bairros/AP/RA (data.rio) e GTFS de trem, metrô, VLT e barcas, para a rede integrada.
