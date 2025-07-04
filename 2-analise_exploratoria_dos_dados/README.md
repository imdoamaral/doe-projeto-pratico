# Análise de Chats de Transmissões ao Vivo no YouTube em uma Subcomunidade Gamer de Humor Negro

**Projeto de TCC 1 - Análise Exploratória dos Dados**

* **Aluno:** Israel Matias do Amaral
* **Orientadora:** Helen

---

## 1. Releitura dos objetivos com eventuais atualizações

### 1.1 Objetivos do estudo

#### Como era:
* Aplicar e comparar modelos de linguagem para detectar discurso de ódio em português, em comentários extraídos de chats ao vivo do Youtube.
* Avaliar o impacto do pré-processamento textual no desempenho dos classificadores.
* Analisar a ocorrência de linguagem velada, ambígua ou irônica em comentários ofensivos.
* Relacionar padrões de toxicidade ao engajamento e perfil dos canais.

#### Como ficou:
* Entender como um classificador de toxicidade do estado da arte classifica os comentários desta sub comunidade.
* Entender como um classificador lida com linguagem ambígua e codificada.
* Expor possíveis riscos do discurso tóxico/ofensivo mascarado como humor.
* Contribuir para o entendimento dos limites do humor, moderação de conteúdo e liberdade de expressão.

### 1.2 Atualizações

#### Metadados
O script de captura de chat foi atualizado para coletar mais campos (likes, visualizações e comentários pós-live).

```json
{
  "id_video": "-gjtdLApVGM",
  "titulo": "48 HORAS DE LIVE KKKKKKKK",
  "descricao": "💰 DOAÇÕES COM MENSAGEM NA TELA VIA PIX: https://livep...",
  "canal": "REnanPLAY",
  "data_publicacao": "2025-06-27T23:29:35Z",
  "data_inicio_live": "2025-06-28T00:10:25Z",
  "espectadores_atuais": "1389",
  "likes": 567,
  "visualizacoes": 2013,
  "comentarios": 0
}
```

#### Classificação das variáveis
* **Categóricas:** autor, canal, id_video, titulo
* **Quantitativas Discretas:** espectadores_atuais, likes, visualizacoes, comentarios
* **Quantitativas Contínuas:** timestamp, data_publicacao, data_inicio_live
* **Texto Livre:** mensagem, descricao

#### Ferramentas e modelos utilizados
* Será considerado o uso do **Perspective API** para a tarefa de classificação;
* Será considerado o uso do **Llama/Deepseek** (em seus modelos mais leves) para tarefas de classificação no computador pessoal.

#### Técnica principal
Projeto Fatorial 2³ com r replicações, testando 3 fatores manipuláveis:

| Fator                  | Níveis                        |
| :--------------------- | :---------------------------- |
| `modelo_classificador` | BERT vs. LLM                  |
| `tipo_preprocessamento`| Sem vs. com tratamento        |
| `tamanho_base_dados`   | Parcial (Amostra) vs. completo|

#### Fator "Pré-processamento"
* **Nível 1: Pré-processamento Mínimo (Padrão do Modelo)**
* **Nível 2: Pré-processamento Direcionado (Limpeza de Ruído)**
    * Substituição de URLs: Trocar qualquer endereço web por um token genérico como `<URL>`.
    * Substituição de Usuários: Trocar menções (ex: @usuario123) por um token `<USUARIO>`.
    * Normalização de Alongamentos: Reduzir caracteres repetidos em excesso.

#### Tabela fatorial 2³

| Combinação | Fator 1: modelo_classificador | Fator 2: tipo_preprocessamento | Fator 3: tamanho_base_dados |
| :--- | :--- | :--- | :--- |
| 1 | BERT | Mínimo (Padrão) | Parcial (Amostra) |
| 2 | BERT | Mínimo (Padrão) | Completa |
| 3 | BERT | Direcionado (Limpeza de Ruído) | Parcial (Amostra) |
| 4 | BERT | Direcionado (Limpeza de Ruído) | Completa |
| 5 | LLM | Mínimo (Padrão) | Parcial (Amostra) |
| 6 | LLM | Mínimo (Padrão) | Completa |
| 7 | LLM | Direcionado (Limpeza de Ruído) | Parcial (Amostra) |
| 8 | LLM | Direcionado (Limpeza de Ruído) | Completa |

#### Como foi definido quais canais pertencem a essa comunidade gamer?
Primeiramente, o YouTube não possui uma estrutura formal de comunidade baseada em tópicos/assuntos (como o Reddit). Então, por ora, optamos por chamar esses agrupamentos informais no YouTube de "nichos" ou "sub comunidades".
Por fim, através da transcrição de vídeos do próprio YouTube, foi possível definir quais canais pertencem a essa sub comunidade.

#### Caracterização do grupo
* Foi identificado um vídeo viral de 2024 que mapeia e caracteriza os principais streamers dessa sub comunidade (Esse vídeo teve cerca de 200.000 visualizações e foi reagido várias vezes alcançando um total aproximado de 5.000.000 de visualizações).
* A partir da transcrição desse vídeo, foi extraído o nome de todos os streamers explicitamente citados como membros dessa sub comunidade.
* Todo o processo de caracterização foi feito de forma sistematizada e reprodutível. Disponível em: [https://github.com/imdoamaral/TCC-1/tree/master/scripts_auxiliares_e_extras](https://github.com/imdoamaral/TCC-1/tree/master/scripts_auxiliares_e_extras)

| Canal | Inscritos |
| :--- | :--- |
| luangameplay | 1.440.000 |
| renanplay | 151.000 |
| canaldoronaldinho | 98.600 |
| diegosheipado | 37.800 |
| biahkov* | 32.400 |
| fabiojunior | 24.100 |
| cavalao2* | 7.470 |
| wallacegamer | 1.460 |

#### Comentários em sala
Considerações sobre o comentário do colega Richard, na minha primeira apresentação:
* Na ocasião, ele propôs uma boa reflexão: “As expressões veladas/códigos da comunidade seriam tratados como texto tóxico ou não?”
* **R:** A ideia inicial é não rotular como tóxico nem como não tóxico, mas dar o significado da expressão e deixar o rotulador/classificador definir baseado no contexto.
* **Exemplo:** o termo “CP” (Child P\*rn) por si só, não quer dizer nada, ou pode ser apenas um flood. Agora a frase “Eu gosto de CP”, possui um contexto que pode ser considerado inadequado.

---

## 2. Apresentação da análise exploratória dos dados
_Visualizações gráficas, estatísticas descritivas e análise de distribuições_

### Descrição do dataset
* Atualmente se aproxima da marca de 1 milhão de comentários e 100 lives coletadas;
* Porém, para uma análise exploratória preliminar, foi feito um recorte desse conjunto de dados, compreendendo um período de 10 dias:
    * **Período:** 06/06/2025 a 15/06/2025
    * **Total de mensagens:** 264.791
    * **Total de lives:** 30

| Canal | Live Count | Total Mensagens |
| :--- | :--- | :--- |
| REnanPLAY | 6 | 133.031 |
| LUANGAMEPLAY | 4 | 59.992 |
| Diego Sheipado | 8 | 39.490 |
| BiahKov | 5 | 16.968 |
| CAVALÃO 2 | 7 | 15.310 |

### Análise 1: Estatísticas Globais por Transmissão
Variância significativa nas métricas, com médias e medianas indicando possível distribuição assimétrica.

| Variável | Média | Mediana |
| :--- | :--- | :--- |
| `quantidade_mensagens` | 8.826,30 | 3.332,50 |
| `tamanho_mensagem` | 31,81 | 29,89 |
| `tempo_entre_mensagens` | 27,35 | 15,70 |

### Análise 2: Quantidade de mensagens por transmissão

![Histograma da quantidade de mensagens por transmissão](histograma_mensagens_por_live.png)

> **Insight:** A maioria das transmissões tem engajamento moderado, enquanto algumas apresentam volumes excepcionalmente altos, sugerindo a necessidade de considerar outliers em análises futuras.


### Análise 3: Quantidade de mensagens por canal

![Boxplot da quantidade de mensagens por canal](boxplot_mensagens_por_canal.png)

> **Insight:** Os canais mostram padrões variados de engajamento, com alguns exibindo maior volume e variabilidade, enquanto outros mantêm transmissões mais homogêneas.

### Análise 4: Volume de mensagens por canal e dia

![Densidade de mensagens por canal e dia](heatmap_mensagens_por_canal_dia_corrigido.png)

> **Insight:** A visualização revela picos de atividade concentrados em alguns canais e dias, com outros apresentando uma distribuição mais uniforme, sugerindo padrões recorrentes de engajamento.

### Análise 5: Correlação entre Inscritos x Média de Mensagens por Transmissão

![Correlação entre Inscritos e Média de Mensagens por Transmissão](correlacao_inscritos_mensagens.png)

> **Insight:** Há uma correlação positiva fraca entre o número de inscritos e a média de mensagens por transmissão, com R² de 0,11, indicando que apenas 11% da variabilidade nas mensagens pode ser explicada pelos inscritos.

### Análise 6: Verificação de Distribuição Teórica de `quantidade_mensagens`

![Distribuições Ajustadas - Densidade de Probabilidade](distribuicao_teorica_quantidade_mensagens.png)

> **Insight:** Os dados têm uma cauda longa à direita, típica de fenômenos onde poucos eventos extremos dominam (ex.: lives com alto engajamento).

### Análise 7: Nuvem de palavras mais frequentes nos chats
Após a criação de uma lista de stopwords customizada e agressiva (com 168 palavras), foi possível remover o ruído superficial (como "jogo", "live", nomes de streamers) e revelar os termos que caracterizam a cultura e a linguagem interna da comunidade analisada.

> **Aviso:** A nuvem de palavras a seguir contém termos pejorativos, gírias e linguagem que podem ser considerados sensíveis. O objetivo é analisar de forma crítica a cultura de comunicação desses espaços, e não endossar o conteúdo.

![Nuvem de palavras mais frequentes nos chats](nuvem_palavras_final.png)

### Conclusões da análise exploratória
* Diferenças claras de engajamento entre os canais.
* Alguns canais se destacam por alto volume de mensagens e devem ser considerados com cuidado na normalização das análises.
* A presença de transmissões com altíssima interação sugere que será importante:
    * Detectar e avaliar os outliers, tratando-os apenas quando forem inconsistentes com o comportamento esperado do conjunto de dados.
    * Levar em conta o canal nas análises futuras, já que ele pode influenciar os resultados e gerar diferenças no volume de mensagens entre as transmissões.
* Canais menores têm distribuições mais concentradas e previsíveis.
* A distribuição lognormal de `quantidade_mensagens` reforça a necessidade de abordar a assimetria e os outliers, guiando a escolha de métodos estatísticos adequados na próxima fase.

---
## 3. Discussão sobre eventuais mudanças na estratégia ou conjunto de dados

*Conforme a apresentação original, os pontos desta seção foram contemplados na seção 1: "Releitura dos objetivos com eventuais atualizações".*

---
## 4. Demonstração de que os dados estão prontos (ou quase prontos) para a fase de experimentação

* **Cobertura Temporal:** O dataset cobre 10 dias, com 264.791 mensagens e 30 lives, indicando uma amostra significativa para o período analisado.
* **Completude dos Dados - Valores ausentes:** `df.isnull().sum()` mostra 0 ausentes em `timestamp`, `canal`, `id_video`, e `mensagem`, confirmando integridade.
* **Total de linhas:** 264.791, consistente com a contagem total.
* **Variabilidade:** `quantidade_mensagens` varia de 239 a 133.031 (média: 8.826, desvio padrão: 15.321), refletindo ampla gama de engajamento. `tamanho_mensagem_médio` varia de 5 a 120 caracteres (média: 31,81), mostrando diversidade de interações.
* **Consistência:** Todos os `timestamp` foram convertidos com sucesso usando `format='mixed'`, e a distribuição lognormal ajustada valida a estrutura dos dados.
