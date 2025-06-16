# Análise Exploratória de Chats de Transmissões ao Vivo

Este documento resume os gráficos gerados e apresenta as principais conclusões da análise exploratória sobre o volume de mensagens em transmissões ao vivo de diferentes canais da comunidade gamer no YouTube.

---

## Gráfico 1: Histograma da quantidade de mensagens por transmissão

![Histograma](histograma_mensagens_por_live.png)

**O que mostra:**

- A maior parte das transmissões possui até **5.000 mensagens**, mas há casos que ultrapassam **30.000 mensagens**.

**Interpretação:**

- A distribuição é fortemente assimétrica, com uma **cauda longa à direita**.
- A maioria dos canais tem transmissões com volume de mensagens moderado, mas há **casos excepcionais com altíssimo engajamento**.
- Essa assimetria sugere a necessidade de tratamento de outliers ou transformações para normalização.

---

## Gráfico 2: Boxplot da quantidade de mensagens por canal

![Boxplot](boxplot_mensagens_por_canal.png)

**O que mostra:**

- A distribuição da quantidade de mensagens por transmissão, agrupada por canal, ordenada pela mediana decrescente.
- Cada boxplot mostra a mediana, a dispersão (IQR), e possíveis outliers.

**Interpretação:**

- Os canais apresentam padrões distintos de engajamento.
- Canais como REnanPLAY e LUANGAMEPLAY concentram transmissões com **maior volume de mensagens** e **variabilidade interna**.
- Os demais canais possuem transmissões mais **homogêneas** e com **menor volume geral** de mensagens.
- A presença de outliers reforça a necessidade de um olhar cuidadoso sobre valores extremos em análises posteriores.

---

## Gráfico 3: Volume de mensagens por canal e dia (heatmap)

![Heatmap](heatmap_mensagens_por_canal_dia.png)

**O que mostra:**

- A intensidade de mensagens enviadas por dia, separada por canal.
- Tons mais escuros representam maior volume de mensagens em determinado dia e canal.

**Interpretação:**

- Há dias de pico de atividade muito concentrada (ex.: 08/06 para REnanPLAY e LUANGAMEPLAY).
- Canais menores apresentam distribuição mais espalhada, sem grandes concentrações.
- A visualização permite identificar padrões de comportamento recorrente por canal.

---

## Gráfico 4: Volume de mensagens por canal e dia (gráfico de barras)

![Barras](barras_mensagens_por_canal_dia.png)

**O que mostra:**

- Comparação direta do volume de mensagens por dia entre os canais.

**Interpretação:**

- REnanPLAY domina em volume geral ao longo da maioria dos dias.
- LUANGAMEPLAY e Diego Sheipado também apresentam picos relevantes, mas com menos regularidade.
- BiahKov e CAVALÃO 2 mantêm baixa variação e consistência.

---

## Gráfico 5: Tamanho médio das mensagens por canal e dia (heatmap)

![Heatmap](heatmap_tamanho_medio_mensagens.png)

**O que mostra:**

- O tamanho médio das mensagens enviadas por dia, separado por canal.
- Tons mais escuros indicam mensagens mais longas, enquanto tons claros indicam mensagens mais curtas.

**Interpretação:**

- LUANGAMEPLAY apresenta os maiores picos de tamanho médio de mensagens, especialmente entre os dias 08/06 e 10/06.
- Os canais BiahKov e CAVALÃO 2 mantêm um padrão relativamente estável, com mensagens de tamanho médio entre 20 e 30 caracteres.
- REnanPLAY e Diego Sheipado apresentam oscilações, com momentos de mensagens mais concisas intercalados com períodos de maior elaboração textual.
- Essa métrica pode estar relacionada ao tipo de interação do público — comentários curtos podem indicar reatividade, enquanto mensagens mais longas sugerem engajamento explicativo ou conversacional.

---

## Gráfico 6: Nuvem de palavras mais frequentes nos chats

![Nuvem de Palavras](nuvem_palavras_chats.png)

**O que mostra:**

- Representação visual das palavras mais usadas nos chats, com tamanho proporcional à frequência.

## Tabela: 10 Palavras Mais Frequentes

| Palavra         | Frequência |
|-----------------|------------|
| pra             | 5206       |
| vai             | 5047       |
| ai              | 3695       |
| renan           | 3518       |
| kkkkkkkkkkkkkkkk| 3102       |
| opa             | 2930       |
| live            | 2887       |
| tá              | 2881       |
| jogo            | 2636       |
| sheipado        | 2597       |

**Interpretação:**

- A tabela destaca os termos mais recorrentes, reforçando o tom casual e o foco em gaming e interação com streamers.
- "kkkkkkkkkkkkkkkk" reflete o humor característico da comunidade.
- Nomes como "renan" e "sheipado" indicam a relevância de streamers na dinâmica dos chats.

---

## Gráfico 7: Distribuição de mensagens por usuário (PMF)

![Distribuição PMF](distribuicao_mensagens_por_usuario.png)

**O que mostra:**

- No eixo X: número de mensagens enviadas por um usuário.
- No eixo Y: a probabilidade (normalizada) de um usuário ter enviado aquela quantidade de mensagens.

**Interpretação:**

- **Distribuição extremamente assimétrica (long tail):**
  - A maioria esmagadora dos usuários enviou poucas mensagens, concentrando-se entre 1 e 5.
  - Um pequeno grupo de usuários enviou centenas ou até milhares de mensagens.
- **Concentração extrema de atividade:**
  - A frequência cai rapidamente após 5 mensagens, mas valores relevantes persistem até mais de 2000 mensagens.
- **Presença de "superusuários":**
  - Os 5% mais ativos (469 usuários) enviaram pelo menos 128 mensagens cada.
  - Esse grupo pode incluir fãs dedicados, bots ou moderadores, influenciando significativamente a tonalidade e o ritmo da conversa.

---

## Gráfico 8: Comparação entre Canais Grandes e Pequenos

![Comparação](comparacao_canais.png)

**O que mostra:**

- Comparação de três métricas: volume médio de mensagens por live, número médio de mensagens por usuário e tempo médio entre mensagens.
- Os canais são divididos em "Grandes" (top 40% por volume médio) e "Pequenos" (os demais).

**Interpretação:**

- **Volume médio por live:** Canais grandes (19302.30) têm significativamente mais mensagens por live que os pequenos (3588.40), refletindo maior engajamento.
- **Mensagens por usuário:** Valores semelhantes (21.28 para grandes vs. 28.71 para pequenos) sugerem que a diferença de volume vem do número de usuários, não da atividade individual.
- **Tempo médio entre mensagens:** Canais grandes (6.41s) têm interações mais rápidas que os pequenos (28.32s), indicando maior dinamismo.

## Tabela: Canais Grandes e Pequenos

| Categoria | Canais              |
|-----------|---------------------|
| Grandes   | LUANGAMEPLAY, REnanPLAY |
| Pequenos  | BiahKov, CAVALÃO 2, Diego Sheipado |

## Tabela: Critério de Classificação

| Critério                | Descrição                                      |
|--------------------------|------------------------------------------------|
| Quantil 60% do volume médio de mensagens por live | Canais com volume médio acima do 60º percentil são classificados como "grandes"; os abaixo são "pequenos". |

---

## Conclusões Práticas

- **Diferenças claras de engajamento** entre os canais.
- REnanPLAY e LUANGAMEPLAY se destacam por alto volume de mensagens e devem ser considerados com cuidado na normalização das análises.
- A presença de transmissões com altíssima interação sugere que será importante:
  - Detectar e avaliar os outliers, tratando-os apenas quando forem inconsistentes com o comportamento esperado do conjunto de dados
  - Levar em conta o canal nas análises futuras, já que ele pode influenciar os resultados e gerar diferenças no volume de mensagens entre as transmissões
- Canais menores, como BiahKov e CAVALÃO 2, têm distribuições mais concentradas e previsíveis.

---

> Esta análise é parte da entrega 2 do projeto de Análise e Projeto de Experimentos, integrando dados reais coletados via API do YouTube.