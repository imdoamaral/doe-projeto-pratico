# Análise Exploratória

## 1. Releitura dos objetivos com eventuais atualizações

### 1.1 Objetivos da Análise
- Entender como um classificador de toxicidade do estado da arte classifica os comentários desta sub comunidade.
- Entender como um classificador lida com linguagem ambígua e codificada.
- Expor possíveis riscos do discurso tóxico/ofensivo mascarado como humor.
- Contribuir para o entendimento dos limites do humor, moderação de conteúdo e liberdade de expressão.


### 1.2 Atualizações
- **Relevância do tema/Timing:** No início de junho, o assunto ganhou mais relevância após a condenação de um famoso humorista adepto do humor politicamente incorreto.

  ![](captura_tela_condenacao_leo_lins.png)

- **Título alternativo:** “Análise de chats de transmissões ao vivo no Youtube em uma sub comunidade gamer de humor negro”
- **Metadados:** o script de captura de chat foi atualizado para coletar mais campos (likes, visualizaçoes e comentarios pós-live).
- **Considerações sobre o comentário do colega Richard, na minha primeira apresentação:**
  - Na ocasião, ele propôs uma boa reflexão: “As expressões veladas/códigos da comunidade seriam tratados como texto tóxico ou não?”
  - **R:** Não vamos rotular como tóxico nem como não tóxico, vamos dar o significado da expressão e deixar o rotulador/classificador definir baseado no contexto.
  - **Exemplo:** o termo “CP” (Child P*rn) por si só, não quer dizer nada, ou pode ser apenas um flood. Agora a frase “Eu gosto de CP”, possui um contexto que pode ser considerado inadequado.

---

## 2. Apresentação da análise exploratória dos dados: Visualizações gráficas, estatı́sticas descritivas e análise de distribuições

### 2.1 Descrição do Dataset
- Período: 06/06/2025 a 15/06/2025
- Total de mensagens: 264.791
- Total de lives: 30

| Canal         | Live Count | Total Mensagens  |
|---------------|------------|------------------|
| REnanPLAY     | 6          | 133.031          |
| LUANGAMEPLAY  | 4          | 59.992           |
| Diego Sheipado| 8          | 39.490           |
| BiahKov       | 5          | 16.968           |
| CAVALÃO 2     | 7          | 15.310           |

### 2.2 Caracterização (Como eu cheguei a esses 5 canais)
1. Foi identificado um vídeo viral de 2024 que mapeia e caracteriza os principais streamers dessa subcomunidade gamer polêmica do YouTube. [Link](https://youtu.be/dK1ZOCCbEDI?si=Z4ozIZke1aGJxmAQ) (Esse vídeo teve cerca de 200.000 visualizações e foi reagido várias vezes alcançando um total aproximado de 5.000.000 de visualizações)
2. A partir da transcrição do vídeo, foi extraído o nome de todos os streamers explicitamente citados como membros da bolha.
3. De um total de 8 streamers, selecionou-se um top 5 baseando-se num critério de engajamento = quantidade de visualizações em 2025.
4. Posteriormente, após discussão com a orientadora, passou-se a monitorar todos os canais.
5. Todo o processo de caracterização foi feito de forma sistematizada e reprodutível. Disponível em: https://github.com/imdoamaral/TCC-1/tree/master/scripts_auxiliares_e_extras

### 2.3 Classificação das Variáveis

- **Categóricas:** `autor`, `canal`, `id_video`, `titulo`  
  <!-- Variáveis nominais que identificam entidades ou categorias fixas, úteis para agrupamentos e comparações diretas (ex.: boxplots por canal). -->

- **Quantitativas Discretas:** `espectadores_atuais`, `likes`, `visualizacoes`, `comentarios`  
  <!-- Representam contagens inteiras, ideais para análises de frequência e soma (ex.: volume médio por live). -->

- **Quantitativas Contínuas:** `timestamp`, `data_publicacao`, `data_inicio_live`  
  <!-- Permitem medir intervalos de tempo e derivar métricas como `tempo_entre_mensagens`, sendo tratadas como contínuas para cálculos de médias e distribuições. -->

- **Texto Livre:** `mensagem`, `descricao`  
  <!-- Textos não estruturados que podem ser transformados em métricas quantitativas (ex.: contagem de palavras, frequência de termos) ou usados em análises qualitativas (ex.: sentimento). -->

### 2.4 Análises

### Análise 1: Estatísticas Globais por Transmissão

| Variável                  | Média    | Mediana  | Moda    |
|---------------------------|----------|----------|---------|
| quantidade_mensagens      | 8.826,30 | 3.332,50 | N/A     |
| tamanho_mensagem          | 31,81    | 29,89    | N/A     |
| tempo_entre_mensagens     | 27,35    | 15,70    | N/A     |

**Insight:**

- A análise revela uma variação significativa nas métricas por transmissão, com médias e medianas indicando distribuições assimétricas, especialmente em `quantidade_mensagens` e `tempo_entre_mensagens`. A ausência de moda aplicável ("N/A") reflete a diversidade única de cada live, sem padrões repetitivos, destacando a necessidade de focar em medidas centrais como média e mediana para capturar as tendências gerais.

---

### Análise 2: Histograma da quantidade de mensagens por transmissão

![Histograma](histograma_mensagens_por_live.png)  

**O que mostra:**

- A maior parte das transmissões possui até **5.000 mensagens**, mas há casos que ultrapassam **30.000 mensagens**.

**Insight:**

- A distribuição exibe uma forte assimetria com cauda longa à direita, indicando que a maioria das transmissões tem engajamento moderado, enquanto algumas apresentam volumes excepcionalmente altos, sugerindo a necessidade de considerar outliers em análises futuras.

---

### Análise 3: Boxplot da quantidade de mensagens por canal

![Boxplot](boxplot_mensagens_por_canal.png)  

**O que mostra:**

- A distribuição da quantidade de mensagens por transmissão, agrupada por canal, ordenada pela mediana decrescente.
- Cada boxplot mostra a mediana, a dispersão (IQR), e possíveis outliers.

**Insight:**

- Os canais mostram padrões variados de engajamento, com alguns exibindo maior volume e variabilidade, enquanto outros mantêm transmissões mais homogêneas, destacando a influência de outliers na análise geral.

---

### Análise 4: Comparação entre Canais Grandes e Pequenos

### Tabela: Critério de Classificação

| Critério                | Descrição                                      |
|--------------------------|------------------------------------------------|
| Quantil 60% do volume médio de mensagens por live | Um "quantil" ajuda a dividir os canais em grupos com base no volume médio de mensagens por live. Canais que têm mais mensagens do que 60% dos outros são chamados de "grandes"; os que têm menos são considerados "pequenos". |

- **Observação:** Poderia usar a média ou mediana como corte, mas a média pode ser influenciada por valores extremos (outliers), e a mediana divide exatamente ao meio (50%), o que pode não destacar o suficiente os maiores canais.

### Tabela: Canais Grandes e Pequenos

| Categoria | Canais              |
|-----------|---------------------|
| Grandes   | LUANGAMEPLAY, REnanPLAY |
| Pequenos  | BiahKov, CAVALÃO 2, Diego Sheipado |

### Tabela: Comparação 

| Métrica                        | Grandes  | Pequenos |
|--------------------------------|----------|----------|
| Volume médio por live          | 19.302,30| 3.588,40 |
| Mensagens por usuário          | 21,28    | 28,71    |
| Tempo médio entre mensagens (s)| 6,41     | 28,32    |

**Insight:**

- Canais grandes apresentam maior volume de mensagens por live e interações mais rápidas, enquanto a atividade por usuário é semelhante, sugerindo que o engajamento total depende do número de participantes.

---

### Análise 5: Comparação entre Streamers Homens e Mulheres

| Métrica                       | Homens    | Mulheres  |
|-------------------------------|-----------|-----------|
| Volume médio por live         | 9.912,92  | 3.393,60  |
| Mensagens por usuário         | 25,24     | 27,73     |
| Tempo médio entre mensagens (s)| 10,34    | 41,75     |
| Percentual de "kkkk" (%)      | 19,65     | 20,80     |
| Percentual de mensagens com emojis (%) | 2,15    | 3,10      |

**Insight:**

- Homens mostram maior volume e dinamismo nos chats, enquanto mulheres têm interações ligeiramente mais espaçadas e maior uso de emojis, com semelhanças no uso de humor, sugerindo diferenças culturais ou de estilo de interação.

---

### Análise 6: Volume de mensagens por canal e dia (heatmap)

![Heatmap](heatmap_mensagens_por_canal_dia_corrigido.png)  

**O que mostra:**

- A intensidade de mensagens enviadas por dia, separada por canal.
- Tons mais escuros representam maior volume de mensagens em determinado dia e canal.

**Insight:**

- A visualização revela picos de atividade concentrados em alguns canais e dias, com outros apresentando uma distribuição mais uniforme, sugerindo padrões recorrentes de engajamento.

---

### Análise 7: Nuvem de palavras mais frequentes nos chats (Análise Refinada)

Após a criação de uma lista de *stopwords* customizada e agressiva (com 168 palavras), foi possível remover o ruído superficial (como "jogo", "live", nomes de streamers) e revelar os termos que caracterizam a cultura e a linguagem interna das comunidades analisadas.

![Nuvem de Palavras Refinada](nuvem_palavras_final.png)

### Tabela: 10 Palavras Mais Frequentes (Após Limpeza)

| Palavra | Frequência |
| :--- | :--- |
| cp | 2093 |
| gay | 1051 |
| mulher | 845 |
| msol | 731 |
| lixo | 670 |
| pai | 588 |
| burro | 582 |
| ri | 573 |
| humor | 530 |
| deus | 525 |

**Insight:**

- A análise refinada vai muito além do tom casual de gaming. A remoção estratégica de stopwords revelou os verdadeiros pilares da comunicação nessas comunidades, que incluem:
    - **Códigos e Gírias Internas:** A alta frequência de `cp` e `msol` confirma a existência de uma linguagem codificada, compreendida apenas pelos membros da subcultura.
    - **Identidade e Temas Sociais:** Palavras como `gay`, `mulher`, `pai` e `deus` são extremamente frequentes, indicando que as conversas giram em torno de identidade, gênero, relações familiares e até religião, temas muito mais profundos do que o esperado.
    - **Tom Conflituoso:** A presença massiva de termos pejorativos como `lixo` e `burro` no topo da lista aponta para uma cultura de confronto, "trollagem" ou um humor agressivo como parte central da interação.
    - **Humor como Conceito:** Em vez de risadas (`kkk`), agora aparecem as palavras `humor` e `ri`, mostrando que o tema ainda é relevante, mas de uma forma mais conceitual na análise.

---

### Análise 8: Tamanho médio das mensagens por canal e dia (heatmap)

![Heatmap](heatmap_tamanho_medio_mensagens_corrigido.png)  

**O que mostra:**

- O tamanho médio das mensagens enviadas por dia, separado por canal.
- Tons mais escuros indicam mensagens mais longas, enquanto tons claros indicam mensagens mais curtas.

**Insight:**

- A análise destaca variações no tamanho médio das mensagens entre canais e períodos, sugerindo que o tipo de interação (reativa ou conversacional) pode influenciar a dinâmica dos chats.

---

### Análise 9: Verificação de Distribuição Teórica de quantidade_mensagens

![](distribuicao_teorica_quantidade_mensagens.png)

**O que mostra:**

- Uma análise foi feita para verificar qual distribuição teórica melhor se ajusta à quantidade de mensagens por transmissão. Foram testadas distribuições como lognormal (lognorm), normal (norm), exponencial (expon), Weibull mínima (weibull_min), e gama (gamma).
- A saída do fitter indicou que a distribuição lognormal foi a melhor ajuste.

**Insight:**
- A distribuição lognormal reflete a assimetria observada no histograma (Análise 2), onde a maioria das transmissões tem poucas mensagens, mas algumas têm valores muito altos. 
- Isso confirma que os dados têm uma cauda longa à direita, típica de fenômenos onde poucos eventos extremos dominam (ex.: lives com alto engajamento).

---

### Análise 10: Correlação entre Inscritos e Média de Mensagens por Transmissão

![Correlação](correlacao_inscritos_mensagens.png)  

**O que mostra:**

- Um gráfico de dispersão que relaciona o número de inscritos (eixo X) com a média de mensagens por transmissão (eixo Y) para os canais analisados.
- Uma linha de tendência vermelha (R² = 0,11) mostra a relação geral entre as variáveis.

**Insight:**

- Há uma correlação positiva fraca entre o número de inscritos e a média de mensagens por transmissão, com R² de 0,11, indicando que apenas 11% da variabilidade nas mensagens pode ser explicada pelos inscritos.
- Canais com mais inscritos tendem a ter médias de mensagens mais altas, mas a dispersão sugere que outros fatores (ex.: conteúdo ou interação do streamer) influenciam fortemente o engajamento.

---

## 3. Discussão sobre eventuais mudanças na estratégia ou conjunto de dados
- O conjunto de dados passará a contar com mais streamers
- O monitoramento e a coleta de lives continuará por tempo indefinido
---

## 4. Demonstração de que os dados estão prontos (ou quase prontos) para a fase de experimentação.

- **Cobertura Temporal:** O dataset cobre 10 dias, com 264.791 mensagens e 30 lives, indicando uma amostra significativa para o período analisado.
- **Completude dos Dados - Valores ausentes:** df.isnull().sum() mostra 0 ausentes em timestamp, canal, id_video, e mensagem, confirmando integridade.
- **Total de linhas:** 264.791, consistente com a contagem total.
- **Variabilidade:** quantidade_mensagens varia de 239 a 133.031 (média: 8.826, desvio padrão: 15.321), refletindo ampla gama de engajamento.
- **tamanho_mensagem_médio:** varia de 5 a 120 caracteres (média: 31,81), mostrando diversidade de interações.
- **Consistência:** Todos os timestamp foram convertidos com sucesso usando format='mixed', e a distribuição lognormal ajustada valida a estrutura dos dados.

#### Conclusão: Os dados estão quase prontos, com cobertura adequada e variabilidade esperada. A ausência de valores ausentes e a consistência dos formatos suportam a transição para a próxima fase, com ajustes menores a serem implementados.
---

## 5. Conclusões

- **Diferenças claras de engajamento** entre os canais.
- Alguns canais se destacam por alto volume de mensagens e devem ser considerados com cuidado na normalização das análises.
- A presença de transmissões com altíssima interação sugere que será importante:
  - Detectar e avaliar os outliers, tratando-os apenas quando forem inconsistentes com o comportamento esperado do conjunto de dados.
  - Levar em conta o canal nas análises futuras, já que ele pode influenciar os resultados e gerar diferenças no volume de mensagens entre as transmissões.
- Canais menores têm distribuições mais concentradas e previsíveis.
- A análise por gênero revela diferenças no dinamismo e uso de emojis, sugerindo variações culturais ou de interação que podem ser exploradas em estudos futuros.
- A distribuição lognormal de quantidade_mensagens reforça a necessidade de abordar a assimetria e os outliers, guiando a escolha de métodos estatísticos adequados na próxima fase.

---

> Esta análise é parte da entrega 2 do projeto de Análise e Projeto de Experimentos, integrando dados reais coletados via API do YouTube.