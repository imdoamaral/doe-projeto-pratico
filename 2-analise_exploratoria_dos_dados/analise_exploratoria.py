import pandas as pd
import matplotlib.pyplot as plt
import pytz
import numpy as np
from wordcloud import WordCloud
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# # Download de recursos do NLTK (executar somente na primeira vez que rodar o script)
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('stopwords')

# Carrega dataset
df = pd.read_csv("/home/israel/Documentos/GitHub/dataset_unificado.csv")
df['canal'] = df['canal'].astype(str).str.strip()

# Calcula o tamanho de cada mensagem (em caracteres)
df['tamanho_mensagem'] = df['mensagem'].str.len()

# Criação global de quantidade_mensagens
mensagens_por_live = df.groupby('id_video').size().reset_index(name='quantidade_mensagens')
canal_por_live = df[['id_video', 'canal']].drop_duplicates()
mensagens_por_live = mensagens_por_live.merge(canal_por_live, on='id_video')
mensagens_por_live = mensagens_por_live[mensagens_por_live['quantidade_mensagens'] > 0]
df = df.merge(mensagens_por_live[['id_video', 'quantidade_mensagens']], on='id_video', how='left')

# # HISTOGRAMA - MENSAGENS POR LIVE
# plt.hist(mensagens_por_live['quantidade_mensagens'])
# plt.title("Histograma da quantidade de mensagens por transmissão")
# plt.xlabel("Quantidade de mensagens")
# plt.ylabel("Frequência")
# plt.xlim(left=0)
# plt.ylim(bottom=0)
# plt.grid(False)
# plt.tight_layout()
# plt.savefig("histograma_mensagens_por_live.png", dpi=300)
# plt.close()

# # BOXPLOT - MENSAGENS POR CANAL
# canais = mensagens_por_live['canal'].unique()
# dados_por_canal = [
#     mensagens_por_live[mensagens_por_live['canal'] == canal]['quantidade_mensagens']
#     for canal in canais
# ]
# medianas = [dados_por_canal[i].median() for i in range(len(canais))]
# canais_ordenados = [canais[i] for i in sorted(range(len(medianas)), key=lambda x: medianas[x], reverse=True)]
# dados_ordenados = [dados_por_canal[i] for i in sorted(range(len(medianas)), key=lambda x: medianas[x], reverse=True)]
# plt.boxplot(dados_ordenados, tick_labels=canais_ordenados)
# plt.title("Boxplot da quantidade de mensagens por canal")
# plt.xlabel("Canal")
# plt.ylabel("Mensagens por transmissão")
# plt.ylim(bottom=0)
# plt.grid(axis='y', linestyle='dashed')
# plt.grid(axis='x', visible=False)
# plt.xticks(ticks=range(1, len(canais_ordenados) + 1), labels=canais_ordenados, rotation=45, ha='right', va='top')
# plt.tight_layout()
# plt.savefig("boxplot_mensagens_por_canal.png", dpi=300)
# plt.close()

# # HEATMAP - MENSAGENS POR CANAL E DIA
# df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
# df['dia'] = df['timestamp'].dt.date
# mensagens_por_dia = df.groupby(['canal', 'dia']).size().reset_index(name='quantidade_mensagens')
# pivot_data = mensagens_por_dia.pivot(index='canal', columns='dia', values='quantidade_mensagens').fillna(0)

# plt.figure()
# plt.imshow(pivot_data, aspect='auto', cmap='YlOrRd')
# plt.title('Densidade de mensagens por canal e dia')
# plt.xlabel('Dia')
# plt.ylabel('Canal')
# plt.xticks(ticks=range(len(pivot_data.columns)), 
#            labels=[f"{pd.to_datetime(d).day:02d}/{pd.to_datetime(d).month:02d}" for d in pivot_data.columns], 
#            rotation=45, ha='right')
# plt.yticks(ticks=range(len(pivot_data.index)), labels=pivot_data.index)
# plt.colorbar(label='Quantidade de mensagens')
# plt.tight_layout()
# plt.savefig("heatmap_mensagens_por_canal_dia_corrigido.png", dpi=300)
# plt.close()

# # HEATMAP - TAMANHO MÉDIO DAS MENSAGENS (CONTEXTO GLOBAL)
# df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True)
# tz_local = pytz.timezone('America/Sao_Paulo')
# df['timestamp_local'] = df['timestamp'].dt.tz_convert(tz_local)
# tamanho_medio_por_dia = df.groupby(['canal', df['timestamp_local'].dt.date])['tamanho_mensagem'].mean().reset_index()
# pivot_data = tamanho_medio_por_dia.pivot(index='canal', columns='timestamp_local', values='tamanho_mensagem').fillna(0)

# plt.figure()
# plt.imshow(pivot_data, aspect='auto', cmap='YlOrRd')
# plt.title('Tamanho médio das mensagens por canal e dia')
# plt.xlabel('Dia')
# plt.ylabel('Canal')
# plt.xticks(ticks=range(len(pivot_data.columns)), 
#            labels=[f"{pd.to_datetime(d).day:02d}/{pd.to_datetime(d).month:02d}" for d in pivot_data.columns], 
#            rotation=45, ha='right')
# plt.yticks(ticks=range(len(pivot_data.index)), labels=pivot_data.index)
# plt.colorbar(label='Tamanho médio (caracteres)')
# plt.tight_layout()
# plt.savefig("heatmap_tamanho_medio_mensagens_corrigido.png", dpi=300)
# plt.close()

# WORDCLOUD - PALAVRAS MAIS FREQUENTES

import re

# ==============================================================================
#                  DEFINIÇÃO DA LISTA DE STOPWORDS CUSTOMIZADAS
# ==============================================================================
# Carrega a lista padrão de stopwords do NLTK.
stop_words = set(stopwords.words('portuguese'))

# ------------------------------------------------------------------------------
# CATEGORIA 1: Conectivos e Palavras de Ligação (Artigos, Preposições, etc.)
# ------------------------------------------------------------------------------
stopwords_conectivos = [
    'pra', 'pro', 'pa', 'q', 'so', 'la', 'lá', 'aí', 'ai', 'entao', 'então', 'assim',
    'aqui', 'tudo', 'nada', 'coisa', 'coisas', 'todo', 'toda'
]

# ------------------------------------------------------------------------------
# CATEGORIA 2: Verbos Comuns e Conjugações
# ------------------------------------------------------------------------------
stopwords_verbos = [
    'ser', 'fazer', 'ir', 'ter', 'dar', 'ver', 'quer', 'dizer', 'falar', 'saber',
    'ficar', 'poder', 'parecer', 'achar', 'comer', 'jogar', 'manda', 'tira', 'pega',
    'vem', 'sai', 'deve', 'acha', 'faz', 'vai', 'tá', 'ta', 'to', 'tô', 'ia', 'era',
    'foi', 'vou', 'falou', 'ficou', 'tava', 'ficar', 'falaro', 'olha', 'toma',
    'parece', 'fala', 'pode', 'come', 'fica', 'sabe', 'quero', 'joga'
]

# ------------------------------------------------------------------------------
# CATEGORIA 3: Adjetivos, Advérbios e Qualificadores Genéricos
# ------------------------------------------------------------------------------
stopwords_adjetivos_adverbios = [
    'bom', 'boa', 'ruim', 'melhor', 'pior', 'maior', 'menor', 'novo', 'real', 'igual',
    'bem', 'mal', 'agora', 'hoje', 'hj', 'ainda', 'nunca', 'sempre', 'demais', 'cedo',
    'noite', 'dia', 'anos', 'quanto', 'linda', 'gostoso', 'podre', 'cade',
    'ja' # <--- MOVIDA DA CAT 1
]

# ------------------------------------------------------------------------------
# CATEGORIA 4: Interjeições, Saudações e Gírias de Interação
# ------------------------------------------------------------------------------
stopwords_interjeicoes_girias = [
    'oi', 'opa', 'eita', 'ah', 'oxi', 'oops', 'sim', 'nao', 'mano', 'cara', 'mané',
    'mlk', 'brabo', 'salve', 'né', 'ne', 'vc', 'mt', 'pq', 'po', 'koe', 'koeee', 'ae',
    'mds', 'tbm', 'gente'
]

# ------------------------------------------------------------------------------
# CATEGORIA 5: Ofensas e Palavrões Comuns
# ------------------------------------------------------------------------------
stopwords_ofensas = [
    'pqp', 'porra', 'merda', 'caralho', 'poha', 'fds', 'krl', 'foda', 'lixeiro'
]

# ------------------------------------------------------------------------------
# CATEGORIA 6: Palavras de Contexto (REMOÇÃO ESTRATÉGICA)
# ------------------------------------------------------------------------------
stopwords_contexto_geral = [
    'live', 'jogo', 'jogos', 'games', 'chat', 'video', 'canal', 'ban'
]
stopwords_contexto_topicos = [
    'filme', 'filmin', 'música', 'musica', 'dinheiro', 'reais', 'medo'
]
stopwords_contexto_streamers = [
    'renan', 'luan', 'renanplay', 'biah', 'cavalo', 'sheipado', 'sheypado',
    'shey', 'shei', 'manso', 'nobre', 'pesco', 'rica', 'cioba', 'tapa', 'américa'
]

# ------------------------------------------------------------------------------
# CATEGORIA 7: Miscelânea e Termos em Outros Idiomas
# ------------------------------------------------------------------------------
stopwords_misc = [
    'https', 'the', 'of', 'resto', 'calma', 'nome'
]

# ------------------------------------------------------------------------------
#                JUNTANDO TODAS AS CATEGORIAS E ATUALIZANDO
# ------------------------------------------------------------------------------
# Junta todas as listas de categorias em uma única lista final.
custom_stop_words = (
    stopwords_conectivos +
    stopwords_verbos +
    stopwords_adjetivos_adverbios +
    stopwords_interjeicoes_girias +
    stopwords_ofensas +
    stopwords_contexto_geral +
    stopwords_contexto_topicos +
    stopwords_contexto_streamers +
    stopwords_misc
)

# Adiciona a sua lista customizada ao conjunto principal de stopwords do NLTK.
# Usar 'update' em um 'set' já garante que não haverá palavras duplicadas.
stop_words.update(custom_stop_words)

print(f"Lista de stopwords customizadas carregada e organizada. Total de {len(custom_stop_words)} palavras adicionadas.")

texto_completo = ' '.join(df['mensagem'].dropna().astype(str).tolist())
palavras = word_tokenize(texto_completo.lower())

palavras_filtradas = []
for palavra in palavras:
    if re.fullmatch(r'k{2,}', palavra):
        continue

    if palavra.isalpha() and len(palavra) > 1 and palavra not in stop_words:
        palavras_filtradas.append(palavra)

# Geração da WordCloud (sem alterações)
frequencia_palavras = nltk.FreqDist(palavras_filtradas)
wordcloud = WordCloud(
    width=1200, 
    height=600, 
    background_color='white', 
    min_font_size=10, 
    colormap='Dark2'
).generate_from_frequencies(frequencia_palavras)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig("nuvem_palavras_final.png", dpi=600)
plt.close()

print("10 palavras mais frequentes (após a limpeza final):")
print(frequencia_palavras.most_common(10))

# # PMF - DISTRIBUIÇÃO DE MENSAGENS POR USUÁRIO
# mensagens_por_usuario = df.groupby('autor').size().reset_index(name='quantidade_mensagens')
# mensagens_por_usuario = mensagens_por_usuario[mensagens_por_usuario['quantidade_mensagens'] > 0]
# total_usuarios = len(mensagens_por_usuario)
# mensagens_por_usuario['pmf'] = mensagens_por_usuario['quantidade_mensagens'] / total_usuarios
# plt.hist(mensagens_por_usuario['quantidade_mensagens'], weights=mensagens_por_usuario['pmf'], bins=50, edgecolor='black')
# plt.title('Distribuição de mensagens por usuário (PMF)')
# plt.xlabel('Quantidade de mensagens por usuário')
# plt.ylabel('Probabilidade')
# plt.xlim(left=0)
# plt.grid(False)
# plt.tight_layout()
# plt.savefig("distribuicao_mensagens_por_usuario.png", dpi=300)
# plt.close()
# quantil_95 = mensagens_por_usuario['quantidade_mensagens'].quantile(0.95)
# superusuarios = mensagens_por_usuario[mensagens_por_usuario['quantidade_mensagens'] >= quantil_95]
# print(f"Número de superusuários (top 5%): {len(superusuarios)}")
# print(f"Quantidade mínima de mensagens para ser superusuário: {quantil_95}")

# # TABELA - COMPARAÇÃO ENTRE CANAIS GRANDES E PEQUENOS
# volume_medio_por_canal = df.groupby('canal')['quantidade_mensagens'].mean().reset_index()
# quantil_60 = volume_medio_por_canal['quantidade_mensagens'].quantile(0.60)  # Ajuste para top 40%
# canais_grandes = volume_medio_por_canal[volume_medio_por_canal['quantidade_mensagens'] >= quantil_60]['canal'].tolist()
# canais_pequenos = volume_medio_por_canal[volume_medio_por_canal['quantidade_mensagens'] < quantil_60]['canal'].tolist()
# print("Canais grandes:", canais_grandes)
# print("Canais pequenos:", canais_pequenos)

# # Volume médio de mensagens por live
# volume_medio_grandes = df[df['canal'].isin(canais_grandes)].groupby('id_video')['quantidade_mensagens'].mean().mean()
# volume_medio_pequenos = df[df['canal'].isin(canais_pequenos)].groupby('id_video')['quantidade_mensagens'].mean().mean()
# print(f"Volume médio por live - Grandes: {volume_medio_grandes:.2f}, Pequenos: {volume_medio_pequenos:.2f}")

# # Número médio de mensagens por usuário
# mensagens_por_usuario = df.groupby(['canal', 'autor']).size().reset_index(name='quantidade_mensagens_usuario')
# mensagens_por_usuario_grandes = mensagens_por_usuario[mensagens_por_usuario['canal'].isin(canais_grandes)].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
# mensagens_por_usuario_pequenos = mensagens_por_usuario[mensagens_por_usuario['canal'].isin(canais_pequenos)].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
# # Substitui NaN por 0 para evitar barras em branco
# mensagens_por_usuario_grandes = 0 if pd.isna(mensagens_por_usuario_grandes) else mensagens_por_usuario_grandes
# mensagens_por_usuario_pequenos = 0 if pd.isna(mensagens_por_usuario_pequenos) else mensagens_por_usuario_pequenos
# print(f"Mensagens por usuário - Grandes: {mensagens_por_usuario_grandes:.2f}, Pequenos: {mensagens_por_usuario_pequenos:.2f}")

# # Tempo médio entre mensagens
# df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
# df = df.sort_values(['canal', 'timestamp'])
# df['tempo_entre_mensagens'] = df.groupby('canal')['timestamp'].diff().dt.total_seconds()
# tempo_medio_grandes = df[df['canal'].isin(canais_grandes)]['tempo_entre_mensagens'].mean()
# tempo_medio_pequenos = df[df['canal'].isin(canais_pequenos)]['tempo_entre_mensagens'].mean()
# # Substitui NaN por 0 para evitar barras em branco
# tempo_medio_grandes = 0 if pd.isna(tempo_medio_grandes) else tempo_medio_grandes
# tempo_medio_pequenos = 0 if pd.isna(tempo_medio_pequenos) else tempo_medio_pequenos
# print(f"Tempo médio entre mensagens (segundos) - Grandes: {tempo_medio_grandes:.2f}, Pequenos: {tempo_medio_pequenos:.2f}")

# # TABELA - COMPARAÇÃO ENTRE TRANSMISSÕES DE STREAMERS HOMENS E MULHERES
# df['genero_streamer'] = df['canal'].apply(lambda x: 'Mulher' if x == 'BiahKov' else 'Homem')

# # Volume médio de mensagens por live
# volume_medio_homens = df[df['genero_streamer'] == 'Homem'].groupby('id_video')['quantidade_mensagens'].mean().mean()
# volume_medio_mulheres = df[df['genero_streamer'] == 'Mulher'].groupby('id_video')['quantidade_mensagens'].mean().mean()
# print(f"Volume médio por live - Homens: {volume_medio_homens:.2f}, Mulheres: {volume_medio_mulheres:.2f}")

# # Intensidade do chat (mensagens por usuário)
# mensagens_por_usuario = df.groupby(['canal', 'autor']).size().reset_index(name='quantidade_mensagens_usuario')
# mensagens_por_usuario_homens = mensagens_por_usuario[mensagens_por_usuario['canal'] != 'BiahKov'].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
# mensagens_por_usuario_mulheres = mensagens_por_usuario[mensagens_por_usuario['canal'] == 'BiahKov'].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
# mensagens_por_usuario_homens = 0 if pd.isna(mensagens_por_usuario_homens) else mensagens_por_usuario_homens
# mensagens_por_usuario_mulheres = 0 if pd.isna(mensagens_por_usuario_mulheres) else mensagens_por_usuario_mulheres
# print(f"Mensagens por usuário - Homens: {mensagens_por_usuario_homens:.2f}, Mulheres: {mensagens_por_usuario_mulheres:.2f}")

# # Tempo médio entre mensagens (intensidade)
# df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
# df = df.sort_values(['canal', 'timestamp'])
# df['tempo_entre_mensagens'] = df.groupby('canal')['timestamp'].diff().dt.total_seconds()
# tempo_medio_homens = df[df['genero_streamer'] == 'Homem']['tempo_entre_mensagens'].mean()
# tempo_medio_mulheres = df[df['genero_streamer'] == 'Mulher']['tempo_entre_mensagens'].mean()
# tempo_medio_homens = 0 if pd.isna(tempo_medio_homens) else tempo_medio_homens
# tempo_medio_mulheres = 0 if pd.isna(tempo_medio_mulheres) else tempo_medio_mulheres
# print(f"Tempo médio entre mensagens (segundos) - Homens: {tempo_medio_homens:.2f}, Mulheres: {tempo_medio_mulheres:.2f}")

# # Uso de termos e emojis (exemplo simplificado: contagem de "kkkk" e emojis)
# df['contem_kkkk'] = df['mensagem'].str.contains('kkkk', case=False, na=False)
# df['contem_emoji'] = df['mensagem'].str.contains('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]', na=False)
# percentual_kkkk_homens = df[df['genero_streamer'] == 'Homem']['contem_kkkk'].mean() * 100
# percentual_kkkk_mulheres = df[df['genero_streamer'] == 'Mulher']['contem_kkkk'].mean() * 100
# percentual_emoji_homens = df[df['genero_streamer'] == 'Homem']['contem_emoji'].mean() * 100
# percentual_emoji_mulheres = df[df['genero_streamer'] == 'Mulher']['contem_emoji'].mean() * 100
# print(f"Percentual de mensagens com 'kkkk' - Homens: {percentual_kkkk_homens:.2f}%, Mulheres: {percentual_kkkk_mulheres:.2f}%")
# print(f"Percentual de mensagens com emojis - Homens: {percentual_emoji_homens:.2f}%, Mulheres: {percentual_emoji_mulheres:.2f}%")

# from fitter import Fitter

# # FITTER - TESTE DE DISTRIBUIÇÃO
# data = mensagens_por_live['quantidade_mensagens'].dropna()

# # Criando o objeto Fitter com distribuições comuns a serem testadas
# f = Fitter(data, distributions=['norm', 'lognorm', 'expon', 'gamma', 'weibull_min'])

# # Ajustando as distribuições aos dados
# f.fit()

# # Exibindo o resumo com as melhores distribuições
# print(f.summary())

# # Exibindo a melhor distribuição encontrada
# print(f"Melhor distribuição: {f.get_best()}")

# # Gerando o gráfico da função de densidade de probabilidade
# f.plot_pdf()
# plt.title('Distribuições Ajustadas - Densidade de Probabilidade')

# # Obtendo os eixos e destacando a distribuição lognormal
# axes = plt.gcf().get_axes()
# for ax in axes:
#     for line in ax.get_lines():
#         label = line.get_label()
#         if 'lognorm' in label.lower():
#             line.set_color('orange')  # Destaca lognormal em azul
#             line.set_linewidth(2)   # Aumenta a espessura
#         else:
#             line.set_color('gray')  # Outras em cinza
#             line.set_alpha(0.3)     # Reduz opacidade

# plt.grid(False)  # Remove os grids
# plt.savefig('distribuicao_teorica_quantidade_mensagens.png', dpi=300, bbox_inches='tight')
# plt.close()  # Fecha a figura para evitar exibição

# from scipy.stats import linregress

# # Dados fornecidos (ajustados para corresponder aos nomes do DataFrame)
# canais = ["BiahKov", "Diego Sheipado", "CAVALÃO 2", "REnanPLAY", "LUANGAMEPLAY"]
# inscritos = [32400, 37800, 7470, 151000, 1440000]

# # Calcular média de mensagens por transmissão a partir do DataFrame
# mensagens_media = df.groupby('canal')['quantidade_mensagens'].mean().reindex(canais).fillna(0).values

# # Verificar os valores calculados
# print("Média de mensagens por canal:", mensagens_media)

# # Realizar regressão linear para linha de tendência
# slope, intercept, r_value, p_value, std_err = linregress(inscritos, mensagens_media)
# line = slope * np.array(inscritos) + intercept

# # Criar o gráfico de dispersão
# plt.figure()
# plt.scatter(inscritos, mensagens_media, color='blue', label='Dados')
# plt.plot(inscritos, line, color='red', label=f'Linha de Tendência (R² = {r_value**2:.2f})')

# # Configurações do gráfico
# plt.xlabel('Inscritos')
# plt.ylabel('Média de Mensagens por Transmissão')
# plt.title('Correlação entre Inscritos e Média de Mensagens por Transmissão')
# plt.legend()
# plt.grid(False)

# # Adicionar rótulos aos pontos
# for i, canal in enumerate(canais):
#     plt.annotate(canal, (inscritos[i], mensagens_media[i]), xytext=(10, -3), textcoords='offset points')

# # Ajustar escalas para melhor visualização
# plt.xticks([151000, 1440000], ['151.000', '1.440.000'])
# plt.ylim(0, max(mensagens_media) * 1.1 if max(mensagens_media) > 0 else 30000)  # Ajuste dinâmico do limite Y

# # Salvar o gráfico
# plt.savefig('correlacao_inscritos_mensagens.png', dpi=300, bbox_inches='tight')
# plt.close()