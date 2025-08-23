# -*- coding: utf-8 -*-
"""
Script final para o experimento fatorial com BERT.

Executa N repetições de Bootstrap do treinamento e calcula o F1-Score médio.
Pode ser configurado para rodar com dados 'bruto' ou 'padrao'.

Os caminhos para os arquivos de dados e de log são definidos dinamicamente
com base na localização do script e incluem um timestamp para evitar sobreescrita.
"""
# --------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# --------------------------------------------------------------------------
import sys
import time
import datetime
import pandas as pd
import torch
import numpy as np
import re
import os
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.utils import resample
from math import isfinite


# --------------------------------------------------------------------------
# 2. CONFIGURAÇÕES GLOBAIS DO EXPERIMENTO
# --------------------------------------------------------------------------

# !! INTERRUPTOR PRINCIPAL !! Altere entre 'bruto' e 'padrao' para cada execução.
TIPO_PREPROCESSAMENTO = 'padrao'

# --- Definição dinâmica dos caminhos dos arquivos ---
# Descobre o caminho absoluto do diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define os nomes base dos arquivos
nome_arquivo_csv = 'amostra_rotulada.csv'

# Cria um timestamp para garantir que o nome do log seja único
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo_log = f'log_bert_{TIPO_PREPROCESSAMENTO}_{timestamp}.txt'

# Constrói o caminho completo para os arquivos
NOME_ARQUIVO_DADOS = os.path.join(script_dir, nome_arquivo_csv)
ARQUIVO_DE_LOG = os.path.join(script_dir, nome_arquivo_log)
# --- Fim da seção de caminhos dinâmicos ---

# Parâmetros do modelo
NOME_COLUNA_TEXTO = 'mensagem'
NOME_COLUNA_ROTULO = 'classificacao_binaria'
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased'

# Parâmetros de treinamento e do experimento
MAX_LENGTH = 128
BATCH_SIZE = 16
TEST_SIZE = 0.15
RANDOM_STATE = 42
EPOCHS = 3
N_REPLICACOES = 30 # Número de repetições do Bootstrap. Sugestão do professor para experimentos futuros: utilizar valores maiores (50, 100...)

# --------------------------------------------------------------------------
# 3. CLASSES E FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------
class Logger(object):
    """Classe para redirecionar a saída (print) para o terminal e um arquivo de log."""
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8') # Usa 'w' (write) para criar um novo arquivo sempre
    def write(self, message):
        self.terminal.write(message); self.log.write(message)
    def flush(self):
        self.terminal.flush(); self.log.flush()

def preprocessamento_padrao(texto: str) -> str:
    """Aplica uma limpeza básica no texto: minúsculas e remoção de quebras de linha."""
    if not isinstance(texto, str): return ""
    texto = texto.lower()
    texto = re.sub(r'[\n\r]+', ' ', texto)
    return texto.strip()

# --------------------------------------------------------------------------
# 4. FUNÇÃO PRINCIPAL DE TREINAMENTO E AVALIAÇÃO
# --------------------------------------------------------------------------
def treinar_e_avaliar(df_amostra: pd.DataFrame, device: torch.device) -> float:
    """Recebe uma amostra do dataframe, treina, avalia o modelo e retorna o melhor F1-Score."""
    textos = df_amostra[NOME_COLUNA_TEXTO].astype(str).tolist()
    rotulos = df_amostra[NOME_COLUNA_ROTULO].tolist()

    tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT, do_lower_case=False)
    
    encoded_data = tokenizer.batch_encode_plus(
        textos, add_special_tokens=True, return_attention_mask=True,
        padding='max_length', max_length=MAX_LENGTH, truncation=True, return_tensors='pt'
    )
    input_ids, attention_masks, labels = encoded_data['input_ids'], encoded_data['attention_mask'], torch.tensor(rotulos)

    train_inputs, val_inputs, train_labels, val_labels, train_masks, val_masks = train_test_split(
        input_ids, labels, attention_masks, random_state=RANDOM_STATE,
        test_size=TEST_SIZE, stratify=labels
    )

    train_data = TensorDataset(train_inputs, train_masks, train_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=BATCH_SIZE)

    val_data = TensorDataset(val_inputs, val_masks, val_labels)
    val_sampler = SequentialSampler(val_data)
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=BATCH_SIZE)

    model = BertForSequenceClassification.from_pretrained(
        NOME_MODELO_BERT, num_labels=2, output_attentions=False, output_hidden_states=False,
    )
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
    total_steps = len(train_dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
    
    best_f1_score = 0.0

    for epoch_i in range(EPOCHS):
        print(f"\n---- Época {epoch_i + 1}/{EPOCHS} ----")

        model.train()
        train_loss = 0.0
        for batch in train_dataloader:
            b_input_ids, b_input_mask, b_labels = [t.to(device) for t in batch]

            optimizer.zero_grad()
            output = model(b_input_ids,
                           attention_mask=b_input_mask,
                           labels=b_labels)
            loss = output.loss
            train_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        avg_train_loss = train_loss / len(train_dataloader)

        model.eval()
        val_loss = 0.0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in val_dataloader:
                b_input_ids, b_input_mask, b_labels = [t.to(device) for t in batch]
                output = model(b_input_ids,
                               attention_mask=b_input_mask,
                               labels=b_labels)

                loss = output.loss
                val_loss += loss.item()

                logits = output.logits
                preds = np.argmax(logits.detach().cpu().numpy(), axis=1)
                labels = b_labels.cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels)

        avg_val_loss = val_loss / len(val_dataloader)
        f1 = f1_score(all_labels, all_preds, pos_label=1, average='binary', zero_division=0)

        print(f"Loss Treino: {avg_train_loss:.4f} | Loss Val: {avg_val_loss:.4f} | F1 Val: {f1:.4f}")

        if f1 > best_f1_score:
            if not np.isfinite(f1):
                f1 = 0.0
            best_f1_score = max(best_f1_score, f1)
       
    return float(best_f1_score)


# --------------------------------------------------------------------------
# 5. ORQUESTRADOR DO EXPERIMENTO
# --------------------------------------------------------------------------
def main():
    """Função principal que orquestra a execução do experimento."""
    try:
        df_original = pd.read_csv(NOME_ARQUIVO_DADOS)
    except FileNotFoundError:
        print(f"ERRO: O arquivo de dados '{os.path.basename(NOME_ARQUIVO_DADOS)}' não foi encontrado.")
        print(f"Por favor, certifique-se de que ele está na mesma pasta que o script.")
        return # Encerra o script se o arquivo de dados não for encontrado

    print(f"Modo de pré-processamento selecionado: '{TIPO_PREPROCESSAMENTO}'")
    if TIPO_PREPROCESSAMENTO == 'padrao':
        print("Aplicando pré-processamento padrão na coluna de mensagens...")
        df_original[NOME_COLUNA_TEXTO] = df_original[NOME_COLUNA_TEXTO].apply(preprocessamento_padrao)
        print("Pré-processamento aplicado com sucesso.\n")
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f'Usando GPU: {torch.cuda.get_device_name(0)}\n')
    else:
        device = torch.device("cpu")
        print('Nenhuma GPU encontrada, usando CPU.\n')

    lista_de_f1_scores = []
    
    print(f"--- Iniciando {N_REPLICACOES} repetições de Bootstrap ---")
    
    for i in range(N_REPLICACOES):
        t0 = time.time()
        print(f"\n--- Repetição {i + 1}/{N_REPLICACOES} ---")
        
        amostra_bootstrap = resample(df_original, replace=True, n_samples=len(df_original), random_state=i)
        
        melhor_f1 = treinar_e_avaliar(amostra_bootstrap, device)
        lista_de_f1_scores.append(melhor_f1)
        
        tempo_da_replica = time.strftime("%H:%M:%S", time.gmtime(time.time() - t0))
        print(f"Melhor F1-Score da repetição: {melhor_f1:.4f}")
        print(f"Tempo da repetição: {tempo_da_replica}")

    f1_medio = np.mean(lista_de_f1_scores)
    f1_std = np.std(lista_de_f1_scores)
    
    print("\n" + "="*50)
    print("---            RESULTADO FINAL DO EXPERIMENTO            ---")
    print("="*50)
    print(f"Modelo: {NOME_MODELO_BERT}")
    print(f"Pré-processamento: {TIPO_PREPROCESSAMENTO}")
    print(f"Número de Replicações: {N_REPLICACOES}")
    print(f"F1-Scores individuais (arredondado): {[round(f, 4) for f in lista_de_f1_scores]}")
    print("\n" + "-"*50)
    print(f"F1-SCORE MÉDIO (BINÁRIO, CLASSE 1): {f1_medio:.4f}")
    print(f"Desvio Padrão dos F1-Scores: {f1_std:.4f}")
    print("="*50)

# --------------------------------------------------------------------------
# 6. PONTO DE ENTRADA DO SCRIPT
# --------------------------------------------------------------------------
if __name__ == '__main__':
    # O Logger é inicializado aqui, usando o nome de arquivo dinâmico definido acima
    sys.stdout = Logger(ARQUIVO_DE_LOG)
    print(f"Iniciando execução do script: {datetime.datetime.now()}")
    print("-" * 30)
    main()
    print("-" * 30)
    print(f"Execução finalizada: {datetime.datetime.now()}")