# Painel "Raio-X dos Ônibus do Rio"

Página privada no Claude (artifact "Raio-X dos Ônibus do Rio", https://claude.ai/artifact/KWYFt3icqX8qboCqxQSLLE). Para outras pessoas abrirem, é preciso compartilhar pelo menu Share da página.

Painel público no GitHub Pages (20/10/2026): https://gabriel-mottagm.github.io/diagnostico_onibus_rio/ — publicado automaticamente da branch `gh-pages` pelo workflow `.github/workflows/pages.yml` a cada mudança em `painel/` no main; fora do Claude, "Baixar CSV" usa o download comum do navegador.

Repositório no GitHub (20/10/2026; renomeado em 21/10/2026): https://github.com/gabriel-mottagm/diagnostico_onibus_rio (antes analyse_bus_network_rio) — scripts do pipeline (`pipeline.sh` reproduz todas as saídas), resultados, painel, seção territorial reservada e documentação.

Versões: v1 (19/10/2026) núcleo · v2 (20/10/2026) moradores por ponto de parada na ficha · v3 (20/10/2026) camadas territoriais e aba Bairros · v4 (20/10/2026) = v2 de novo, camadas e Bairros retirados a pedido do usuário · v5 (20/10/2026) modo técnico · **v6 (20/10/2026) modo técnico sem indicadores territoriais** (versão em produção).

## Decisões do usuário
- Primeiro a versão para a população em geral; depois um modo "análise técnica" (feito).
- Moradores por parada: só na ficha da linha, não como indicador de cor do mapa no modo geral (20/10/2026). No modo técnico aparece como coluna da tabela e do CSV, não como cor do mapa.
- Camadas territoriais e aba Bairros: **fora do produto por enquanto** (20/10/2026). Motivo: muita informação num mapa só. Ideia para depois: um mapa separado, numa outra seção da página, junto com Bairros — formato ainda não decidido.
- Indicadores de perfil da área atendida (% atendidos nos 30% de renda mais baixa e nos 30% de renda mais alta, % pretos e pardos, renda média da área atendida): **retirados do modo técnico** (20/10/2026) por serem do território e não da linha; reservados para a futura seção territorial com camadas e Bairros.

## Modo geral (público)
- Indicadores das linhas: Tempo de espera (por dia e horário), Ônibus por dia, Velocidade, Horário de funcionamento, Moradores perto (400 m a pé), Tamanho do trajeto.
- Filtros: dia (útil, sábado, domingo/feriado), horário (madrugada, pico da manhã, meio do dia, pico da tarde, noite, dia todo), tipo (ônibus, BRT, frescão), busca por número ou bairro.
- Mapa: linhas coloridas pelo indicador (azul = melhor, vermelho = pior; violeta sem juízo de valor), melhor serviço desenhado por cima, legenda com contagem, hover com linha e valor, clique abre a ficha e mostra as paradas.
- Lista ordenável (melhores/piores primeiro), 40 por vez com "Mostrar mais".
- Ficha da linha: letreiro, tipo, operador, tarifa, frase do pico da manhã, tempo de espera por horário × dia, partidas por hora, primeiro e último ônibus, moradores a 5 e 10 min a pé, moradores por ponto de parada, pontos de parada, velocidade e trajeto.
- "Sobre os dados": fontes, o que não aparece e como cada número é calculado.
- Temas claro e escuro; layout de celular.

## Modo técnico (v5/v6)
- Chave "Modo técnico" no cabeçalho (lembrada no navegador do visitante). Desligada, a página é igual ao modo geral.
- 6 indicadores técnicos a mais para colorir o mapa (chips tracejados): Frota estimada (mínima no pico), Quilometragem (km por dia útil), Tortuosidade (menor = melhor; circulares sem valor), Ida ≠ volta (% do trajeto só em um sentido), Moradores a 10 min (800 m a pé), Moradores por partida.
- A lista vira tabela: coluna fixa da linha, colunas escolhidas em "Colunas" (padrão: espera, ônibus por dia, velocidade, frota, moradores perto, moradores por partida; a coluna do indicador ativo sempre aparece), ordenação clicando no cabeçalho, clique na linha abre a ficha.
- Filtros por faixa de valor: indicador + mínimo e/ou máximo; vários filtros combinados (todas as condições). Linhas que não passam ficam apagadas no mapa e saem da tabela e da contagem da legenda. Indicadores por horário usam o dia e horário escolhidos.
- Exportação: "Baixar CSV" (capability `downloads`; o visitante confirma) com 28 colunas para as linhas que passam nos filtros, incluindo tempo de espera de todos os períodos do dia escolhido; vírgula como separador, ponto decimal, UTF-8 com BOM. "Copiar tabela" copia as colunas visíveis (decimal com vírgula).
- Ficha com seção "Indicadores técnicos": frota, km/dia, partidas útil·sáb·dom, tortuosidade, trajeto só em um sentido, moradores por partida, identificador GTFS.
- "Sobre os dados" com definições dos indicadores técnicos, do método do tempo de espera, dos filtros e do CSV.
- Testes (Playwright): modo geral inalterado; tabela com 494 linhas; filtros, ordenação, cópia; CSV simulado; celular sem rolagem horizontal; estado salvo com indicador removido volta ao tempo de espera. O download real só funciona dentro do Claude.

## Moradores por ponto de parada (v2)
- Moradores a até 400 m a pé de alguma parada da linha ÷ pontos de parada (paradas a menos de 100 m umas das outras na mesma linha contam como um ponto).
- Mediana da rede: 1.140; de 32 a 4.311. 474 = 2.070 (88 pontos, 103 paradas); BRT 22 = 988; 232 = 1.347.

## Reservado para a futura seção territorial (camadas + Bairros + perfil da área atendida)
- Camadas (v3): Ônibus perto de casa, Renda e ônibus, Onde falta ônibus, Caminho até o ponto. Aba Bairros: 166 bairros, ficha com cobertura, nível de serviço, caminhada média, renda, pessoas onde falta ônibus e linhas que param.
- Perfil da área atendida por linha (retirado do modo técnico na v6): % atendidos nos 30% de renda mais baixa (neutro = 30%; média das linhas 19%) e nos 30% de renda mais alta (média 42%), % pretos e pardos (cidade = 54%), renda média da área atendida. Os valores estão em `indicadores_linhas.csv` (colunas pct_pop_30pct_renda_mais_baixa, pct_pop_30pct_renda_mais_alta, pct_pretos_pardos, renda_media_area_atendida).
- Arquivos em `reserva_secao_territorial/`: página v3 (camadas + Bairros), página v5 (com os indicadores de perfil), territorio.json, PNGs das camadas, painel_territorio.py (gera esses dados: `python3 painel_territorio.py censo osm ape <destino>`) e patch_v3.py.
- Técnica das camadas: grade de 100 m codificada em PNG e colorida na página com as cores do tema; índice de bairro por quadrícula.

## Ônibus ao vivo (20/10/2026)
- Seção "Agora na rua" na ficha da linha e ônibus no mapa: círculo escuro com seta âmbar na direção do movimento; esmaecido se a posição tem mais de 4 min; some com mais de 10 min. Passando o mouse aparecem o número do ônibus, o sentido, a velocidade e a idade da posição.
- Fonte: API de geolocalização da frota da SMTR (`its.mobilidade.rio`, beta, CC BY 4.0). Atraso de 1 a 2 min; cerca de 10 ônibus e 20 KB por minuto na linha 474. `route_id` no mesmo formato do GTFS.
- Sem CORS na API: intermediário Cloudflare Worker (`cloudflare/worker.js`) com cache de 30 s; o painel consulta a cada 30 s só a linha aberta e para ao fechar a ficha ou com a aba oculta.
- Compara com as partidas programadas para a hora atual (tipo de dia pela data no fuso do Rio, sem feriados).
- Worker publicado em https://rio-onibus-aovivo.gabrielmgmaciel.workers.dev (conta Cloudflare do usuário). Desligado dentro do Claude e se `AOVIVO_URL` estiver vazio.

## Arquitetura técnica
- Página HTML única, mapa em Canvas com código próprio (câmera, linhas, hover, clique, paradas).
- Mapa de fundo (20/10/2026): OpenFreeMap (Positron no tema claro, Dark no escuro; grátis, sem chave, uso comercial permitido), desenhado pelo MapLibre GL JS 4.7.1 (cópia em `painel/vendor/`) embaixo do canvas. O canvas continua dono da câmera; o MapLibre só acompanha (erro de alinhamento medido ≈ 0,1 px). Os dados são convertidos para Web Mercator na carga da página. Crédito no canto do mapa: OpenFreeMap © OpenMapTiles © OpenStreetMap.
- Seletor de fundo no canto superior esquerdo do mapa (20/10/2026): Claro (Positron), Escuro (Dark) ou Simples (fundo próprio). A escolha fica no navegador do visitante (`rxo-fundo`); sem escolha, segue o tema do aparelho. As cores das linhas e da legenda acompanham o fundo (paleta escura sobre o fundo escuro, mesmo com a página clara). Se o OpenFreeMap falhar, Claro e Escuro ficam desativados. O seletor não aparece dentro do Claude.
- Fundo próprio (quando o OpenFreeMap não carrega: dentro do Claude, sem WebGL ou sem rede; desiste após 12 s): contorno da cidade e limites aproximados dos bairros (setores do Censo), vias e trilhos (OSM), rótulos de bairro. Na página do Claude o fundo externo nem é tentado.
- Dados publicados: `data/linhas.json` (~2,1 MB; bloco `tec` por linha com fr, vkm, tort, div, ns, ppp) e `data/contexto.json` (~550 KB). Capability declarada: `downloads`.
- Scripts: `scripts/05_painel/painel_contexto.py`, `scripts/05_painel/painel_linhas.py`.

## Próximas entregas (a decidir com o usuário)
- Seção territorial separada: mapa com as camadas, Bairros e perfil da área atendida por linha.
- Atualização com um GTFS mais recente (o atual vence em 31/12/2026).
