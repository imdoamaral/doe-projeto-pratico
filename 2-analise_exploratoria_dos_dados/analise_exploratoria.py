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

# Criação e mesclagem de quantidade_mensagens (mantida globalmente)
mensagens_por_live = df.groupby('id_video').size().reset_index(name='quantidade_mensagens')
canal_por_live = df[['id_video', 'canal']].drop_duplicates()
mensagens_por_live = mensagens_por_live.merge(canal_por_live, on='id_video')
mensagens_por_live = mensagens_por_live[mensagens_por_live['quantidade_mensagens'] > 0]
df = df.merge(mensagens_por_live[['id_video', 'quantidade_mensagens']], on='id_video', how='left')

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

# DISTRIBUIÇÃO DE MENSAGENS POR USUÁRIO
# Conta mensagens por usuário (usando 'autor' conforme amostra)
mensagens_por_usuario = df.groupby('autor').size().reset_index(name='quantidade_mensagens')

# Calcula PMF
mensagens_por_usuario = mensagens_por_usuario[mensagens_por_usuario['quantidade_mensagens'] > 0]
total_usuarios = len(mensagens_por_usuario)
mensagens_por_usuario['pmf'] = mensagens_por_usuario['quantidade_mensagens'] / total_usuarios

# Histograma da PMF
plt.hist(mensagens_por_usuario['quantidade_mensagens'], weights=mensagens_por_usuario['pmf'], bins=50, edgecolor='black')
plt.title('Distribuição de mensagens por usuário (PMF)')
plt.xlabel('Quantidade de mensagens por usuário')
plt.ylabel('Probabilidade')
plt.xlim(left=0)
plt.grid(False)
plt.tight_layout()
plt.savefig("distribuicao_mensagens_por_usuario.png", dpi=300)
plt.close()

# Identifica superusuários (top 5%)
quantil_95 = mensagens_por_usuario['quantidade_mensagens'].quantile(0.95)
superusuarios = mensagens_por_usuario[mensagens_por_usuario['quantidade_mensagens'] >= quantil_95]
print(f"Número de superusuários (top 5%): {len(superusuarios)}")
print(f"Quantidade mínima de mensagens para ser superusuário: {quantil_95}")

# COMPARAÇÃO ENTRE CANAIS GRANDES E PEQUENOS
# Calcula quantidade de mensagens por id_video e mescla com df
mensagens_por_live = df.groupby('id_video').size().reset_index(name='quantidade_mensagens')
df = df.merge(mensagens_por_live[['id_video', 'quantidade_mensagens']], on='id_video', how='left')

# Classifica canais como grandes ou pequenos (ajusta para quantil 60%)
volume_medio_por_canal = df.groupby('canal')['quantidade_mensagens'].mean().reset_index()
quantil_60 = volume_medio_por_canal['quantidade_mensagens'].quantile(0.60)  # Ajuste para top 40%
canais_grandes = volume_medio_por_canal[volume_medio_por_canal['quantidade_mensagens'] >= quantil_60]['canal'].tolist()
canais_pequenos = volume_medio_por_canal[volume_medio_por_canal['quantidade_mensagens'] < quantil_60]['canal'].tolist()
print("Canais grandes:", canais_grandes)
print("Canais pequenos:", canais_pequenos)

# Volume médio de mensagens por live
volume_medio_grandes = df[df['canal'].isin(canais_grandes)].groupby('id_video')['quantidade_mensagens'].mean().mean()
volume_medio_pequenos = df[df['canal'].isin(canais_pequenos)].groupby('id_video')['quantidade_mensagens'].mean().mean()
print(f"Volume médio por live - Grandes: {volume_medio_grandes:.2f}, Pequenos: {volume_medio_pequenos:.2f}")

# Número médio de mensagens por usuário
mensagens_por_usuario = df.groupby(['canal', 'autor']).size().reset_index(name='quantidade_mensagens_usuario')
mensagens_por_usuario_grandes = mensagens_por_usuario[mensagens_por_usuario['canal'].isin(canais_grandes)].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
mensagens_por_usuario_pequenos = mensagens_por_usuario[mensagens_por_usuario['canal'].isin(canais_pequenos)].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
# Substitui NaN por 0 para evitar barras em branco
mensagens_por_usuario_grandes = 0 if pd.isna(mensagens_por_usuario_grandes) else mensagens_por_usuario_grandes
mensagens_por_usuario_pequenos = 0 if pd.isna(mensagens_por_usuario_pequenos) else mensagens_por_usuario_pequenos
print(f"Mensagens por usuário - Grandes: {mensagens_por_usuario_grandes:.2f}, Pequenos: {mensagens_por_usuario_pequenos:.2f}")

# Tempo médio entre mensagens
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.sort_values(['canal', 'timestamp'])
df['tempo_entre_mensagens'] = df.groupby('canal')['timestamp'].diff().dt.total_seconds()
tempo_medio_grandes = df[df['canal'].isin(canais_grandes)]['tempo_entre_mensagens'].mean()
tempo_medio_pequenos = df[df['canal'].isin(canais_pequenos)]['tempo_entre_mensagens'].mean()
# Substitui NaN por 0 para evitar barras em branco
tempo_medio_grandes = 0 if pd.isna(tempo_medio_grandes) else tempo_medio_grandes
tempo_medio_pequenos = 0 if pd.isna(tempo_medio_pequenos) else tempo_medio_pequenos
print(f"Tempo médio entre mensagens (segundos) - Grandes: {tempo_medio_grandes:.2f}, Pequenos: {tempo_medio_pequenos:.2f}")

# Depuração: Verifica valores antes do gráfico
print("Valores Grandes:", [volume_medio_grandes, mensagens_por_usuario_grandes, tempo_medio_grandes])
print("Valores Pequenos:", [volume_medio_pequenos, mensagens_por_usuario_pequenos, tempo_medio_pequenos])

# Gráfico de barras comparativo
metricas = ['Volume médio/live', 'Mensagens/usuário', 'Tempo médio entre msgs (s)']
valores_grandes = [volume_medio_grandes, mensagens_por_usuario_grandes, tempo_medio_grandes]
valores_pequenos = [volume_medio_pequenos, mensagens_por_usuario_pequenos, tempo_medio_pequenos]
x = np.arange(len(metricas))
width = 0.35

bars1 = plt.bar(x - width/2, valores_grandes, width, label='Grandes', color='blue')
bars2 = plt.bar(x + width/2, valores_pequenos, width, label='Pequenos', color='orange')
plt.ylabel('Valores')
plt.title('Comparação entre Canais Grandes e Pequenos')
plt.xticks(x, metricas)
plt.legend()
plt.yscale('symlog')
plt.ylim(1, max(max(valores_grandes), max(valores_pequenos)) * 2)
# Adiciona rótulos nas barras
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}',
                 ha='center', va='bottom' if height > 0 else 'top')

plt.tight_layout()
plt.savefig("comparacao_canais.png", dpi=300)
plt.close()

# COMPARAÇÃO ENTRE TRANSMISSÕES DE STREAMERS HOMENS E MULHERES
# Classifica canais por gênero (BiahKov como mulher, outros como homens)
df['genero_streamer'] = df['canal'].apply(lambda x: 'Mulher' if x == 'BiahKov' else 'Homem')

# Volume médio de mensagens por live
volume_medio_homens = df[df['genero_streamer'] == 'Homem'].groupby('id_video')['quantidade_mensagens'].mean().mean()
volume_medio_mulheres = df[df['genero_streamer'] == 'Mulher'].groupby('id_video')['quantidade_mensagens'].mean().mean()
print(f"Volume médio por live - Homens: {volume_medio_homens:.2f}, Mulheres: {volume_medio_mulheres:.2f}")

# Intensidade do chat (mensagens por usuário)
mensagens_por_usuario = df.groupby(['canal', 'autor']).size().reset_index(name='quantidade_mensagens_usuario')
mensagens_por_usuario_homens = mensagens_por_usuario[mensagens_por_usuario['canal'] != 'BiahKov'].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
mensagens_por_usuario_mulheres = mensagens_por_usuario[mensagens_por_usuario['canal'] == 'BiahKov'].groupby('canal')['quantidade_mensagens_usuario'].mean().mean()
mensagens_por_usuario_homens = 0 if pd.isna(mensagens_por_usuario_homens) else mensagens_por_usuario_homens
mensagens_por_usuario_mulheres = 0 if pd.isna(mensagens_por_usuario_mulheres) else mensagens_por_usuario_mulheres
print(f"Mensagens por usuário - Homens: {mensagens_por_usuario_homens:.2f}, Mulheres: {mensagens_por_usuario_mulheres:.2f}")

# Tempo médio entre mensagens (intensidade)
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.sort_values(['canal', 'timestamp'])
df['tempo_entre_mensagens'] = df.groupby('canal')['timestamp'].diff().dt.total_seconds()
tempo_medio_homens = df[df['genero_streamer'] == 'Homem']['tempo_entre_mensagens'].mean()
tempo_medio_mulheres = df[df['genero_streamer'] == 'Mulher']['tempo_entre_mensagens'].mean()
tempo_medio_homens = 0 if pd.isna(tempo_medio_homens) else tempo_medio_homens
tempo_medio_mulheres = 0 if pd.isna(tempo_medio_mulheres) else tempo_medio_mulheres
print(f"Tempo médio entre mensagens (segundos) - Homens: {tempo_medio_homens:.2f}, Mulheres: {tempo_medio_mulheres:.2f}")

# Uso de termos e emojis (exemplo simplificado: contagem de "kkkk" e emojis)
df['contem_kkkk'] = df['mensagem'].str.contains('kkkk', case=False, na=False)
df['contem_emoji'] = df['mensagem'].str.contains('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]', na=False)
percentual_kkkk_homens = df[df['genero_streamer'] == 'Homem']['contem_kkkk'].mean() * 100
percentual_kkkk_mulheres = df[df['genero_streamer'] == 'Mulher']['contem_kkkk'].mean() * 100
percentual_emoji_homens = df[df['genero_streamer'] == 'Homem']['contem_emoji'].mean() * 100
percentual_emoji_mulheres = df[df['genero_streamer'] == 'Mulher']['contem_emoji'].mean() * 100
print(f"Percentual de mensagens com 'kkkk' - Homens: {percentual_kkkk_homens:.2f}%, Mulheres: {percentual_kkkk_mulheres:.2f}%")
print(f"Percentual de mensagens com emojis - Homens: {percentual_emoji_homens:.2f}%, Mulheres: {percentual_emoji_mulheres:.2f}%")

# Gráfico de barras comparativo
metricas = ['Volume médio/live', 'Mensagens/usuário', 'Tempo médio (s)', 'kkkk (%)', 'Emojis (%)']
valores_homens = [volume_medio_homens, mensagens_por_usuario_homens, tempo_medio_homens, percentual_kkkk_homens, percentual_emoji_homens]
valores_mulheres = [volume_medio_mulheres, mensagens_por_usuario_mulheres, tempo_medio_mulheres, percentual_kkkk_mulheres, percentual_emoji_mulheres]
x = np.arange(len(metricas))
width = 0.35

bars1 = plt.bar(x - width/2, valores_homens, width, label='Homens', color='blue')
bars2 = plt.bar(x + width/2, valores_mulheres, width, label='Mulheres', color='orange')
plt.ylabel('Valores')
plt.title('Comparação entre Streamers Homens e Mulheres')
plt.xticks(x + width/2, metricas, rotation=45, ha='right')  # Centraliza xticks entre barras
plt.legend()
plt.yscale('symlog')
plt.ylim(1, max(max(valores_homens), max(valores_mulheres)) * 1.5)
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}',  # Reduzido para 1 casa decimal
                 ha='center', va='bottom' if height > 0 else 'top', fontsize=8)  # Reduzido tamanho da fonte

plt.tight_layout()
plt.savefig("comparacao_genero.png", dpi=300)
plt.close()