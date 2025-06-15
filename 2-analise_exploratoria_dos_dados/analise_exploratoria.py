import pandas as pd
import matplotlib.pyplot as plt
import pytz
import numpy as np
from wordcloud import WordCloud
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download de recursos do NLTK (executar no início)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# Carrega dataset
df = pd.read_csv("dataset_unificado.csv")
df['canal'] = df['canal'].astype(str).str.strip()

# Calcula o tamanho de cada mensagem (em caracteres)
df['tamanho_mensagem'] = df['mensagem'].str.len()

# Contagem de mensagens por transmissão
mensagens_por_live = df.groupby('id_video').size().reset_index(name='quantidade_mensagens')
canal_por_live = df[['id_video', 'canal']].drop_duplicates()
mensagens_por_live = mensagens_por_live.merge(canal_por_live, on='id_video')
mensagens_por_live = mensagens_por_live[mensagens_por_live['quantidade_mensagens'] > 0]

# HISTOGRAMA
plt.hist(mensagens_por_live['quantidade_mensagens'])
plt.title("Histograma da quantidade de mensagens por transmissão")
plt.xlabel("Quantidade de mensagens")
plt.ylabel("Frequência")
# Certifica de que os zeros do eixo x e y comecem no mesmo lugar
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.grid(False)
plt.tight_layout()
plt.savefig("histograma_mensagens_por_live.png", dpi=300)
plt.close()

# BOXPLOT
canais = mensagens_por_live['canal'].unique()
dados_por_canal = [
    mensagens_por_live[mensagens_por_live['canal'] == canal]['quantidade_mensagens']
    for canal in canais
]

# Calcular medianas para ordenação
medianas = [dados_por_canal[i].median() for i in range(len(canais))]
# Ordenar canais por mediana decrescente
canais_ordenados = [canais[i] for i in sorted(range(len(medianas)), key=lambda x: medianas[x], reverse=True)]
dados_ordenados = [dados_por_canal[i] for i in sorted(range(len(medianas)), key=lambda x: medianas[x], reverse=True)]

plt.boxplot(dados_ordenados, tick_labels=canais_ordenados)
plt.title("Boxplot da quantidade de mensagens por canal")
plt.xlabel("Canal")
plt.ylabel("Mensagens por transmissão")
plt.ylim(bottom=0)
plt.grid(axis='y', linestyle='dashed')
plt.grid(axis='x', visible=False)
plt.xticks(ticks=range(1, len(canais_ordenados) + 1), labels=canais_ordenados, rotation=45, ha='right', va='top')
plt.tight_layout()
plt.savefig("boxplot_mensagens_por_canal.png", dpi=300)
plt.close()

# HEATMAP
# Converte timestamp para datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Agrupa por canal e dia
df['dia'] = df['timestamp'].dt.date
mensagens_por_dia = df.groupby(['canal', 'dia']).size().reset_index(name='quantidade_mensagens')

# Pivota para heatmap
pivot_data = mensagens_por_dia.pivot(index='canal', columns='dia', values='quantidade_mensagens').fillna(0)

# Converter colunas (dias) para timezone local (UTC-3)
tz_local = pytz.timezone('America/Sao_Paulo')
pivot_data.columns = [tz_local.localize(pd.Timestamp(d)).date() for d in pivot_data.columns]

# Plot
plt.figure()
plt.imshow(pivot_data, aspect='auto', cmap='YlOrRd')
plt.title('Densidade de mensagens por canal e dia')
plt.xlabel('Dia')
plt.ylabel('Canal')
# Ajustar xticks para mostrar dd/mm, centralizar e evitar sobreposição
plt.xticks(ticks=range(len(pivot_data.columns)), labels=[f"{d.day:02d}/{d.month:02d}" for d in pivot_data.columns], rotation=45, ha='center', va='center')
plt.tick_params(axis='x', length=5, width=1, pad=10)  # Adiciona tracinhos e espaçamento
plt.yticks(ticks=range(len(pivot_data.index)), labels=pivot_data.index)
plt.colorbar(label='Quantidade de mensagens')
plt.tight_layout()
plt.savefig("heatmap_mensagens_por_canal_dia.png", dpi=300)
plt.close()

# MENSAGENS POR CANAL E DIA
# Converte timestamp para datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Agrupa por canal e dia, somando as mensagens
df['dia'] = df['timestamp'].dt.date
mensagens_por_dia = df.groupby(['canal', 'dia']).size().reset_index(name='quantidade_mensagens')

# Pivot para barras agrupadas
pivot_data = mensagens_por_dia.pivot(index='dia', columns='canal', values='quantidade_mensagens').fillna(0)

# Converter índice para timezone local (UTC-3)
tz_local = pytz.timezone('America/Sao_Paulo')
pivot_data.index = [tz_local.localize(pd.Timestamp(d)).date() for d in pivot_data.index]

# Plot
pivot_data.plot(kind='bar')
plt.title('Volume de mensagens por canal e dia')
plt.xlabel('Dia')
plt.ylabel('Quantidade de mensagens')
# Ajustar xticks para mostrar dd/mm, centralizar e evitar sobreposição
plt.xticks(ticks=range(len(pivot_data.index)), labels=[f"{d.day:02d}/{d.month:02d}" for d in pivot_data.index], rotation=45, ha='center', va='center')
plt.tick_params(axis='x', length=5, width=1, pad=10)  # Adiciona tracinhos e espaçamento
plt.legend(title='Canal')
plt.tight_layout()
plt.savefig("barras_mensagens_por_canal_dia.png", dpi=300)
plt.close()

# TAMANHO MÉDIO DAS MENSAGENS (CONTEXTO GLOBAL)
# Converte timestamp para datetime com formato ISO8601
df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True)

# Converte para timezone local (UTC-3)
tz_local = pytz.timezone('America/Sao_Paulo')
df['timestamp_local'] = df['timestamp'].dt.tz_convert(tz_local)

# HEATMAP GLOBAL POR DIA E TAMANHO MÉDIO
tamanho_medio_por_dia = df.groupby(['canal', df['timestamp_local'].dt.date])['tamanho_mensagem'].mean().reset_index()
pivot_data = tamanho_medio_por_dia.pivot(index='canal', columns='timestamp_local', values='tamanho_mensagem').fillna(0)
tz_local = pytz.timezone('America/Sao_Paulo')
pivot_data.columns = [tz_local.localize(pd.Timestamp(d)).date() for d in pivot_data.columns]
plt.figure()
plt.imshow(pivot_data, aspect='auto', cmap='YlOrRd')
plt.title('Tamanho médio das mensagens por canal e dia')
plt.xlabel('Dia')
plt.ylabel('Canal')
# Ajustar xticks para mostrar dd/mm, centralizar e evitar sobreposição
plt.xticks(ticks=range(len(pivot_data.columns)), labels=[f"{d.day:02d}/{d.month:02d}" for d in pivot_data.columns], rotation=45, ha='center', va='center')
plt.tick_params(axis='x', length=5, width=1, pad=10)  # Adiciona tracinhos e espaçamento
plt.yticks(ticks=range(len(pivot_data.index)), labels=pivot_data.index)
plt.colorbar(label='Tamanho médio (caracteres)')
plt.tight_layout()
plt.savefig("heatmap_tamanho_medio_mensagens.png", dpi=300)
plt.close()

# ANÁLISE DO VOCABULÁRIO: PALAVRAS MAIS FREQUENTES
# Combina todas as mensagens em um único texto
texto_completo = ' '.join(df['mensagem'].dropna().astype(str).tolist())

# Tokenização e remoção de stopwords
stop_words = set(stopwords.words('portuguese'))
palavras = word_tokenize(texto_completo.lower())
# Filtra apenas palavras alfanuméricas (letras) com pelo menos 2 caracteres
palavras_filtradas = [palavra for palavra in palavras if palavra.isalpha() and len(palavra) > 1 and palavra not in stop_words]

# Conta a frequência das palavras
frequencia_palavras = nltk.FreqDist(palavras_filtradas)

# Gera a nuvem de palavras com configurações padrão e colormap ajustado
wordcloud = WordCloud(width=1200, height=600, background_color='white', min_font_size=10, colormap='Dark2').generate_from_frequencies(frequencia_palavras)

# Plota a nuvem de palavras
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
# plt.title('Nuvem de palavras mais frequentes nos chats')
plt.axis('off')
plt.tight_layout()
plt.savefig("nuvem_palavras_chats.png", dpi=600)
plt.close()

# Mostra as 10 palavras mais frequentes (opcional)
print("10 palavras mais frequentes:")
print(frequencia_palavras.most_common(10))