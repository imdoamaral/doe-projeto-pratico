import pandas as pd
import numpy as np
import re
import time
import os
import datetime
from sklearn.metrics import f1_score, confusion_matrix
from tqdm import tqdm
from googleapiclient import discovery
from googleapiclient.errors import HttpError

# --- PARÂMETROS DO EXPERIMENTO ---
API_KEY = "SUA_CHAVE_API_AQUI" # IMPORTANTE: Insira sua chave da API aqui

# --- Definição dinâmica dos caminhos ---
script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

ARQUIVO_ROTULADO = os.path.join(script_dir, "amostra_rotulada.csv")
ARQUIVO_LOG = os.path.join(script_dir, f"log_experimento_persp_api_{timestamp}.txt")
# --- Fim da definição dinâmica ---

N_REPLICACOES = 30
LIMIAR_TOXICIDADE = 0.60

# --- INÍCIO DO LOG ---
log_output = []
log_output.append("--- INÍCIO DO LOG DO EXPERIMENTO (PERSPECTIVE API) ---")
log_output.append(f"Data de execução: {pd.Timestamp.now()}")
log_output.append("-" * 30)

# --- FUNÇÕES ---

def preprocessamento_padrao(texto):
    if not isinstance(texto, str): return ""
    texto = texto.lower()
    texto = re.sub(r'[\n\r]+', ' ', texto)
    return texto.strip()

def obter_predicoes_api(dataframe, api_key):
    # (O conteúdo desta função permanece o mesmo)
    client = discovery.build("commentanalyzer", "v1alpha1", developerKey=api_key, static_discovery=False)
    textos = dataframe['mensagem_processada'].tolist()
    predicoes = []
    scores = []

    print(f"Iniciando {len(textos)} chamadas à Perspective API...")
    log_output.append(f"\nIniciando {len(textos)} chamadas à Perspective API...")
    for texto in tqdm(textos, desc="Consultando API"):
        if not texto:
            predicoes.append(0)
            scores.append(0.0)
            continue

        analyze_request = {'comment': {'text': texto}, 'requestedAttributes': {'TOXICITY': {}}, 'languages': ['pt']}
        
        try:
            response = client.comments().analyze(body=analyze_request).execute()
            score = response['attributeScores']['TOXICITY']['summaryScore']['value']
            predicao = 1 if score > LIMIAR_TOXICIDADE else 0
            predicoes.append(predicao)
            scores.append(score)
        except HttpError as e:
            error_msg = f"Erro na API para o texto: '{texto[:30]}...'. Erro: {e}. Assumindo predição 'Não Tóxico'."
            print(error_msg)
            log_output.append(error_msg)
            predicoes.append(0)
            scores.append(-1.0)

        time.sleep(1.1) # Pausa para não exceder o limite de requisições da API
    
    return predicoes, scores

# --- EXECUÇÃO DO EXPERIMENTO ---

try:
    print("Carregando dados rotulados...")
    df_original = pd.read_csv(ARQUIVO_ROTULADO)
except FileNotFoundError:
    print(f"\nERRO: O arquivo de dados '{os.path.basename(ARQUIVO_ROTULADO)}' não foi encontrado.")
    print(f"Por favor, certifique-se de que ele está na mesma pasta que o script.")
    exit() # Encerra o script se o arquivo não for encontrado

df_original['mensagem'] = df_original['mensagem'].astype(str)

# Prepara os dataframes
df_bruto = df_original.copy()
df_bruto['mensagem_processada'] = df_bruto['mensagem']
df_padrao = df_original.copy()
df_padrao['mensagem_processada'] = df_padrao['mensagem'].apply(preprocessamento_padrao)

# Obtém as predições e scores
df_bruto['predicao_api'], df_bruto['score_api'] = obter_predicoes_api(df_bruto, API_KEY)
df_padrao['predicao_api'], df_padrao['score_api'] = obter_predicoes_api(df_padrao, API_KEY)

# Realiza o Bootstrap
resultados = {"bruto": [], "padrao": []}
print("\n--- Iniciando simulação Bootstrap ---")
for df, nome_cenario in [(df_bruto, "bruto"), (df_padrao, "padrao")]:
    for i in tqdm(range(N_REPLICACOES), desc=f"Bootstrap ({nome_cenario.capitalize()})"):
        amostra = df.sample(n=len(df), replace=True, random_state=i)
        # Usando o F1-Score binário, focado na classe 1 (Tóxico)
        f1 = f1_score(amostra['classificacao_binaria'], amostra['predicao_api'], pos_label=1, average='binary', zero_division=0)
        resultados[nome_cenario].append(f1)

# --- ANÁLISE E LOG DOS RESULTADOS FINAIS ---

media_bruto = np.mean(resultados["bruto"])
std_bruto = np.std(resultados["bruto"])
media_padrao = np.mean(resultados["padrao"])
std_padrao = np.std(resultados["padrao"])

# Prepara as strings para o log, agora incluindo a lista completa de scores
log_final = [
    "\n\n" + "="*50,
    "---      RESULTADO FINAL DO EXPERIMENTO (PERSPECTIVE API)      ---",
    "="*50,
    f"Pré-processamento: Bruto",
    f"F1-Scores individuais (arredondado): {[round(f, 4) for f in resultados['bruto']]}",
    f"F1-SCORE MÉDIO (BINÁRIO, CLASSE 1): {media_bruto:.4f}",
    f"Desvio Padrão dos F1-Scores: {std_bruto:.4f}",
    "-"*50,
    f"Pré-processamento: Padrão",
    f"F1-Scores individuais (arredondado): {[round(f, 4) for f in resultados['padrao']]}",
    f"F1-SCORE MÉDIO (BINÁRIO, CLASSE 1): {media_padrao:.4f}",
    f"Desvio Padrão dos F1-Scores: {std_padrao:.4f}",
    "="*50
]

# Imprime na tela e adiciona ao log principal
for line in log_final:
    print(line)
    log_output.append(line)

# --- SALVA O ARQUIVO DE LOG ---
log_output.append("\n--- FIM DO LOG ---")
try:
    with open(ARQUIVO_LOG, 'w', encoding='utf-8') as f:
        f.write("\n".join(log_output))
    print(f"\nLog completo do experimento salvo em: '{ARQUIVO_LOG}'")
except Exception as e:
    print(f"\nERRO ao salvar o arquivo de log: {e}")