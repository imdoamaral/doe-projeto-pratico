# -*- coding: utf-8 -*-
"""
Script de teste para uma ÚNICA execução de treinamento do modelo BERT.
Este script serve para depuração e testes rápidos.
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
import os
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from math import isfinite

# --------------------------------------------------------------------------
# 2. CONFIGURAÇÕES GLOBAIS
# --------------------------------------------------------------------------
# --- Definição dinâmica dos caminhos dos arquivos ---
script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

NOME_ARQUIVO_DADOS = os.path.join(script_dir, 'amostra_rotulada.csv')
ARQUIVO_DE_LOG = os.path.join(script_dir, f'log_teste_treino_unico_{timestamp}.txt')

# Parâmetros do modelo e colunas
NOME_COLUNA_TEXTO = 'mensagem'
NOME_COLUNA_ROTULO = 'classificacao_binaria'
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased'

# Parâmetros de treinamento
MAX_LENGTH = 128
BATCH_SIZE = 16
TEST_SIZE = 0.15
RANDOM_STATE = 42
EPOCHS = 3

# --------------------------------------------------------------------------
# 3. CLASSES E FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------
class Logger(object):
    """Redireciona a saída (print) para o terminal e um arquivo de log."""
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')
    def write(self, message):
        self.terminal.write(message); self.log.write(message)
    def flush(self):
        self.terminal.flush(); self.log.flush()

def format_time(elapsed):
    """Converte tempo em segundos para o formato hh:mm:ss."""
    return str(datetime.timedelta(seconds=int(round(elapsed))))

# --------------------------------------------------------------------------
# 4. FUNÇÃO PRINCIPAL DO SCRIPT
# --------------------------------------------------------------------------
def main():
    """Orquestra o carregamento dos dados, treinamento e validação do modelo."""
    
    # --- FASE 1: Carregamento e Preparação dos Dados ---
    print("--- FASE 1: Carregando e preparando os dados ---")
    try:
        df = pd.read_csv(NOME_ARQUIVO_DADOS)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{os.path.basename(NOME_ARQUIVO_DADOS)}' não encontrado.")
        print(f"Certifique-se de que ele está na pasta: {script_dir}")
        return

    textos = df[NOME_COLUNA_TEXTO].astype(str).tolist()
    rotulos = df[NOME_COLUNA_ROTULO].tolist()

    tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT)

    encoded_data = tokenizer.batch_encode_plus(
        textos, add_special_tokens=True, return_attention_mask=True,
        padding='max_length', max_length=MAX_LENGTH, truncation=True, return_tensors='pt'
    )
    input_ids, attention_masks, labels = encoded_data['input_ids'], encoded_data['attention_mask'], torch.tensor(rotulos)

    train_inputs, val_inputs, train_labels, val_labels, train_masks, val_masks = train_test_split(
        input_ids, labels, attention_masks, random_state=RANDOM_STATE, test_size=TEST_SIZE, stratify=labels
    )
    
    train_data = TensorDataset(train_inputs, train_masks, train_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=BATCH_SIZE)

    val_data = TensorDataset(val_inputs, val_masks, val_labels)
    val_sampler = SequentialSampler(val_data)
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=BATCH_SIZE)
    print("Dados prontos e organizados em DataLoaders.\n")

    # --- FASE 2: Treinamento e Validação ---
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f'Usando dispositivo: {device}\n')

    model = BertForSequenceClassification.from_pretrained(NOME_MODELO_BERT, num_labels=2)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
    total_steps = len(train_dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    print(f"--- FASE 2: Iniciando o treinamento por {EPOCHS} épocas ---")
    
    for epoch_i in range(0, EPOCHS):
        print(f'\n======== Época {epoch_i + 1} / {EPOCHS} ========')
        t0 = time.time()
        
        # Treinamento
        model.train()
        train_loss = 0
        for batch in train_dataloader:
            b_input_ids, b_input_mask, b_labels = [t.to(device) for t in batch]
            optimizer.zero_grad()
            output = model(b_input_ids, attention_mask=b_input_mask, labels=b_labels)
            loss = output.loss
            train_loss += loss.item()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
        avg_train_loss = train_loss / len(train_dataloader)

        # Validação
        model.eval()
        val_loss, all_preds, all_labels = 0, [], []
        with torch.no_grad():
            for batch in val_dataloader:
                b_input_ids, b_input_mask, b_labels = [t.to(device) for t in batch]
                output = model(b_input_ids, attention_mask=b_input_mask, labels=b_labels)
                loss = output.loss
                val_loss += loss.item()
                preds = np.argmax(output.logits.detach().cpu().numpy(), axis=1)
                labels = b_labels.cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels)

        avg_val_loss = val_loss / len(val_dataloader)
        
        f1 = f1_score(all_labels, all_preds, pos_label=1, average='binary', zero_division=0)
        
        epoch_time = format_time(time.time() - t0)
        print(f"Tempo da Época: {epoch_time}")
        print(f"Loss Treino: {avg_train_loss:.4f} | Loss Val: {avg_val_loss:.4f} | F1 Val (Binário): {f1:.4f}")

    print("\n--- Treinamento Concluído! ---")

# --------------------------------------------------------------------------
# 5. PONTO DE ENTRADA DO SCRIPT
# --------------------------------------------------------------------------
if __name__ == '__main__':
    sys.stdout = Logger(ARQUIVO_DE_LOG)
    print(f"Iniciando execução do script de treino único: {datetime.datetime.now()}")
    print("-" * 30)
    main()
    print("-" * 30)
    print(f"Execução finalizada: {datetime.datetime.now()}")
