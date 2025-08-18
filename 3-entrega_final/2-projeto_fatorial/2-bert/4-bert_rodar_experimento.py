# -*- coding: utf-8 -*-
"""
Script final para o experimento fatorial com BERT.

Executa N repetições de Bootstrap do treinamento e calcula o F1-Score médio.
Pode ser configurado para rodar com dados 'bruto' ou 'padrao'.
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
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.utils import resample

# --------------------------------------------------------------------------
# 2. CONFIGURAÇÕES GLOBAIS DO EXPERIMENTO
# --------------------------------------------------------------------------

# !! INTERRUPTOR PRINCIPAL !! Altere entre 'bruto' e 'padrao' para cada execução.
TIPO_PREPROCESSAMENTO = 'bruto'

# Parâmetros do dataset e do modelo
NOME_ARQUIVO_DADOS = 'amostra_rotulada.csv'
NOME_COLUNA_TEXTO = 'mensagem'
NOME_COLUNA_ROTULO = 'classificacao_binaria'
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased'
ARQUIVO_DE_LOG = f'log_experimento_bert_{TIPO_PREPROCESSAMENTO}.txt'

# Parâmetros de treinamento e do experimento
MAX_LENGTH = 128
BATCH_SIZE = 16
TEST_SIZE = 0.15
RANDOM_STATE = 42
EPOCHS = 3
N_REPLICACOES = 30 # Número de repetições do Bootstrap

# --------------------------------------------------------------------------
# 3. CLASSES E FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------
class Logger(object):
    """Classe para redirecionar a saída (print) para o terminal e um arquivo de log."""
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding='utf-8')
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

    # Carrega o tokenizador específico do modelo. 'do_lower_case=False' é importante
    # pois estamos usando um modelo 'cased' que diferencia maiúsculas de minúsculas.
    tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT, do_lower_case=False)
    
    encoded_data = tokenizer.batch_encode_plus(
        textos, add_special_tokens=True, return_attention_mask=True,
        padding='max_length', max_length=MAX_LENGTH, truncation=True, return_tensors='pt'
    )
    input_ids, attention_masks, labels = encoded_data['input_ids'], encoded_data['attention_mask'], torch.tensor(rotulos)

    # Divisão em treino e validação. 'stratify=labels' garante que a proporção
    # de classes seja a mesma em ambos os conjuntos, crucial para dados desbalanceados.
    train_inputs, val_inputs, train_labels, val_labels, train_masks, val_masks = train_test_split(
        input_ids, labels, attention_masks, random_state=RANDOM_STATE,
        test_size=TEST_SIZE, stratify=labels
    )

    # Criação dos DataLoaders para carregar os dados em lotes
    train_data = TensorDataset(train_inputs, train_masks, train_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=BATCH_SIZE)

    val_data = TensorDataset(val_inputs, val_masks, val_labels)
    val_sampler = SequentialSampler(val_data)
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=BATCH_SIZE)

    # Carrega o modelo BERT pré-treinado com uma cabeça de classificação
    model = BertForSequenceClassification.from_pretrained(
        NOME_MODELO_BERT, num_labels=2, output_attentions=False, output_hidden_states=False,
    )
    model.to(device) # Envia o modelo para a GPU (ou CPU)

    # Define o otimizador e o agendador da taxa de aprendizado
    optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
    total_steps = len(train_dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
    
    best_f1_score = 0.0

    # Loop de treinamento por N épocas
    for epoch_i in range(0, EPOCHS):
        print(f"    -> Treinando Época {epoch_i + 1}/{EPOCHS}...")
        model.train()
        for batch in train_dataloader:
            b_input_ids, b_input_mask, b_labels = batch[0].to(device), batch[1].to(device), batch[2].to(device)
            model.zero_grad()
            output = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
            loss = output.loss
            loss.backward() # Realiza o backpropagation para calcular os gradientes
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        # Fase de validação
        model.eval() # Ativa o modo de avaliação (desliga camadas como dropout)
        all_preds, all_labels = [], []
        
        # 'torch.no_grad()' desativa o cálculo de gradientes, economizando memória e tempo
        with torch.no_grad():
            for batch in val_dataloader:
                b_input_ids, b_input_mask, b_labels = batch[0].to(device), batch[1].to(device), batch[2].to(device)
                output = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
                logits = output.logits
                preds = np.argmax(logits.detach().cpu().numpy(), axis=1).flatten()
                labels = b_labels.cpu().numpy().flatten()
                all_preds.extend(preds); all_labels.extend(labels)
            
        # Calcula o F1-Score da época atual e guarda o melhor resultado
        # 'zero_division=0' evita avisos caso uma classe não tenha predições
        f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
        if f1 > best_f1_score:
            best_f1_score = f1
            
    return best_f1_score

# --------------------------------------------------------------------------
# 5. ORQUESTRADOR DO EXPERIMENTO
# --------------------------------------------------------------------------
def main():
    """Função principal que orquestra a execução do experimento."""
    df_original = pd.read_csv(NOME_ARQUIVO_DADOS)
    
    # Aplica o pré-processamento condicionalmente
    print(f"Modo de pré-processamento selecionado: '{TIPO_PREPROCESSAMENTO}'")
    if TIPO_PREPROCESSAMENTO == 'padrao':
        print("Aplicando pré-processamento padrão na coluna de mensagens...")
        df_original[NOME_COLUNA_TEXTO] = df_original[NOME_COLUNA_TEXTO].apply(preprocessamento_padrao)
        print("Pré-processamento aplicado com sucesso.\n")
    
    # Define o dispositivo de hardware (GPU ou CPU)
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f'Usando GPU: {torch.cuda.get_device_name(0)}\n')
    else:
        device = torch.device("cpu")
        print('Nenhuma GPU encontrada, usando CPU.\n')

    lista_de_f1_scores = []
    
    print(f"--- Iniciando {N_REPLICACOES} repetições de Bootstrap ---")
    
    # Loop principal do Bootstrap
    for i in range(N_REPLICACOES):
        t0 = time.time()
        print(f"\n--- Repetição {i + 1}/{N_REPLICACOES} ---")
        
        # Gera uma nova amostra dos dados com reposição
        amostra_bootstrap = resample(df_original, replace=True, n_samples=len(df_original), random_state=i)
        
        # Roda o ciclo completo de treino e avaliação para a amostra
        melhor_f1 = treinar_e_avaliar(amostra_bootstrap, device)
        lista_de_f1_scores.append(melhor_f1)
        
        tempo_da_replica = time.strftime("%H:%M:%S", time.gmtime(time.time() - t0))
        print(f"Melhor F1-Score da repetição: {melhor_f1:.4f}")
        print(f"Tempo da repetição: {tempo_da_replica}")

    # Consolidação e apresentação dos resultados finais
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
    print(f"F1-SCORE MÉDIO (MACRO): {f1_medio:.4f}")
    print(f"Desvio Padrão dos F1-Scores: {f1_std:.4f}")
    print("="*50)

# --------------------------------------------------------------------------
# 6. PONTO DE ENTRADA DO SCRIPT
# --------------------------------------------------------------------------
if __name__ == '__main__':
    # Redireciona a saída (stdout) para o nosso logger antes de executar o main
    sys.stdout = Logger(ARQUIVO_DE_LOG)
    print(f"Iniciando execução do script: {datetime.datetime.now()}")
    print("-" * 30)
    main() # Executa a função principal
    print("-" * 30)
    print(f"Execução finalizada: {datetime.datetime.now()}")