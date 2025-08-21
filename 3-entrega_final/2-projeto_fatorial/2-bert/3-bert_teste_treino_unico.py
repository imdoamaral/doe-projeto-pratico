# -*- coding: utf-8 -*-
"""
Script de treino de teste para o experimento com BERT.
Passos:
1. Carrega e tokeniza os dados.
2. Divide os dados em conjuntos de treino e validação.
3. Cria DataLoaders para alimentar o modelo de forma eficiente.
4. Define e executa o loop de treinamento e validação.
5. Salva toda a saída em um arquivo de log.
"""
import sys
import time
import datetime
import pandas as pd
import torch
import numpy as np
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# --- CLASSE PARA GERAR O LOG ---
# Esta classe redireciona toda a saída do print para um arquivo de log,
# mantendo também a exibição no terminal. Essencial para registrar os resultados.
class Logger(object):
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# --- 1. CONFIGURAÇÕES GLOBAIS ---
# Centraliza todos os parâmetros do experimento para fácil modificação.
NOME_ARQUIVO_DADOS = 'amostra_rotulada.csv'
NOME_COLUNA_TEXTO = 'mensagem'
NOME_COLUNA_ROTULO = 'classificacao_binaria'
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased' # Modelo pré-treinado para português do Brasil.
ARQUIVO_DE_LOG = 'log_treinamento_bert.txt'
MAX_LENGTH = 128      # Comprimento máximo das sentenças. Textos maiores serão truncados.
BATCH_SIZE = 16       # Número de exemplos em cada lote de treinamento.
TEST_SIZE = 0.15      # Proporção do dataset a ser usada para validação.
RANDOM_STATE = 42     # Semente para reprodutibilidade dos resultados.
EPOCHS = 3            # Número de vezes que o modelo verá todo o dataset de treino.

# --- 2. FUNÇÕES AUXILIARES ---
def format_time(elapsed):
    """Converte tempo em segundos para o formato hh:mm:ss."""
    elapsed_rounded = int(round((elapsed)))
    return str(datetime.timedelta(seconds=elapsed_rounded))

# --- 3. FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
def preparar_e_organizar_dados():
    """
    Carrega os dados do CSV, tokeniza os textos usando o tokenizador do BERT
    e organiza tudo em DataLoaders do PyTorch para treino e validação.
    """
    print("--- FASE 1: Carregando, preparando e organizando os dados ---")
    
    # Carrega o dataset a partir de um arquivo CSV.
    df = pd.read_csv(NOME_ARQUIVO_DADOS)
    textos = df[NOME_COLUNA_TEXTO].astype(str).tolist()
    rotulos = df[NOME_COLUNA_ROTULO].tolist()

    # Carrega o tokenizador específico do modelo BERT escolhido.
    print(f"Carregando tokenizador do modelo: {NOME_MODELO_BERT}")
    tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT)

    # Tokeniza todos os textos. `batch_encode_plus` é uma forma eficiente de processar múltiplos textos.
    #   - `add_special_tokens=True`: Adiciona tokens especiais como [CLS] e [SEP].
    #   - `return_attention_mask=True`: Gera a máscara de atenção para que o modelo ignore os paddings.
    #   - `padding='max_length'`: Preenche sentenças menores que MAX_LENGTH com tokens de padding.
    #   - `truncation=True`: Trunca sentenças maiores que MAX_LENGTH.
    #   - `return_tensors='pt'`: Retorna os dados como tensores do PyTorch.
    encoded_data = tokenizer.batch_encode_plus(
        textos, add_special_tokens=True, return_attention_mask=True,
        padding='max_length', max_length=MAX_LENGTH, truncation=True, return_tensors='pt'
    )

    input_ids = encoded_data['input_ids']
    attention_masks = encoded_data['attention_mask']
    labels = torch.tensor(rotulos)

    # Divide os dados em conjuntos de treino e validação.
    # `stratify=labels` garante que a proporção de classes seja a mesma nos dois conjuntos.
    train_inputs, val_inputs, train_labels, val_labels, train_masks, val_masks = train_test_split(
        input_ids, labels, attention_masks, random_state=RANDOM_STATE,
        test_size=TEST_SIZE, stratify=labels
    )

    # Cria um TensorDataset, que é uma forma de agrupar os tensores de entrada, máscaras e rótulos.
    train_data = TensorDataset(train_inputs, train_masks, train_labels)
    # O RandomSampler seleciona os dados de forma aleatória para o treinamento, o que ajuda o modelo a generalizar.
    train_sampler = RandomSampler(train_data)
    # O DataLoader organiza os dados em lotes (batches) para alimentar o modelo de forma eficiente.
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=BATCH_SIZE)

    val_data = TensorDataset(val_inputs, val_masks, val_labels)
    # O SequentialSampler apenas percorre os dados de validação em ordem.
    val_sampler = SequentialSampler(val_data)
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=BATCH_SIZE)

    print("Dados prontos e organizados em DataLoaders.\n")
    return train_dataloader, val_dataloader

# --- 4. FUNÇÃO PRINCIPAL DO SCRIPT ---
def main():
    """
    Função principal que orquestra o treinamento e a validação do modelo.
    """
    train_dataloader, val_dataloader = preparar_e_organizar_dados()

    # Verifica se uma GPU está disponível e a seleciona; caso contrário, usa a CPU.
    # Treinar em GPU é significativamente mais rápido.
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f'Usando GPU: {torch.cuda.get_device_name(0)}\n')
    else:
        device = torch.device("cpu")
        print('Nenhuma GPU encontrada, usando CPU.\n')

    # Carrega o modelo BertForSequenceClassification pré-treinado.
    # `num_labels=2` indica que é uma tarefa de classificação binária.
    model = BertForSequenceClassification.from_pretrained(
        NOME_MODELO_BERT, num_labels=2, output_attentions=False, output_hidden_states=False,
    )
    # Envia o modelo para o dispositivo selecionado (GPU ou CPU).
    model.to(device)

    # Otimizador AdamW é uma variação do Adam recomendada para modelos Transformer.
    optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
    
    # O scheduler ajusta a taxa de aprendizado ao longo do treinamento,
    # o que pode levar a uma convergência melhor e mais estável.
    total_steps = len(train_dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    print(f"--- FASE 2: Iniciando o treinamento por {EPOCHS} épocas ---")
    
    # Loop principal de treinamento.
    for epoch_i in range(0, EPOCHS):
        print(f'\n======== Época {epoch_i + 1} / {EPOCHS} ========')
        print('Treinando...')
        t0 = time.time()
        total_train_loss = 0
        
        # Coloca o modelo em modo de treinamento.
        model.train()

        # Loop sobre cada lote de dados do DataLoader de treino.
        for step, batch in enumerate(train_dataloader):
            # Mostra o progresso a cada 40 lotes.
            if step % 40 == 0 and not step == 0:
                elapsed = format_time(time.time() - t0)
                print(f'  Lote {step:>5} de {len(train_dataloader):>5}. Tempo: {elapsed}.')

            # Desempacota o lote e envia os tensores para a GPU/CPU.
            b_input_ids, b_input_mask, b_labels = batch[0].to(device), batch[1].to(device), batch[2].to(device)
            
            # Zera os gradientes calculados na iteração anterior.
            model.zero_grad()
            
            # Forward pass: passa os dados pelo modelo para obter a saída (logits) e a perda (loss).
            output = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
            loss = output.loss
            total_train_loss += loss.item()
            
            # Backward pass: calcula os gradientes da perda em relação aos parâmetros do modelo.
            loss.backward()
            
            # "Corta" os gradientes para evitar que explodam, um problema comum em redes neurais profundas.
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0);
            
            # Atualiza os pesos do modelo usando o otimizador.
            optimizer.step()
            
            # Atualiza a taxa de aprendizado.
            scheduler.step()

        avg_train_loss = total_train_loss / len(train_dataloader)
        training_time = format_time(time.time() - t0)
        print(f"\n  Média da perda de treino: {avg_train_loss:.4f}")
        print(f"  Tempo de treino da época: {training_time}")

        # --- Loop de Validação ---
        print("\nValidando...")
        t0 = time.time()
        
        # Coloca o modelo em modo de avaliação. Camadas como Dropout se comportam de forma diferente.
        model.eval()
        all_preds, all_labels = [], []

        for batch in val_dataloader:
            b_input_ids, b_input_mask, b_labels = batch[0].to(device), batch[1].to(device), batch[2].to(device)
            
            # `torch.no_grad()` desativa o cálculo de gradientes, economizando memória e acelerando a validação.
            with torch.no_grad():
                output = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
            
            # A saída do modelo (logits) são as pontuações brutas para cada classe.
            logits = output.logits
            # `np.argmax` seleciona a classe com a maior pontuação como a predição do modelo.
            preds = np.argmax(logits.detach().cpu().numpy(), axis=1).flatten()
            labels = b_labels.cpu().numpy().flatten()
            
            # Armazena as predições e rótulos de todos os lotes para calcular a métrica final.
            all_preds.extend(preds)
            all_labels.extend(labels)
            
        # Calcula o F1-Score, uma métrica robusta para classificação desbalanceada.
        f1 = f1_score(all_labels, all_preds, average='macro')
        print(f"  F1-Score (Macro) na validação: {f1:.4f}")
        validation_time = format_time(time.time() - t0)
        print(f"  Tempo de validação: {validation_time}")

    print("\n--- Treinamento Concluído! ---")

# Ponto de entrada do script.
if __name__ == '__main__':
    # Redireciona a saída padrão (stdout) para o nosso logger.
    # Isso garante que tudo que é impresso na tela seja salvo no arquivo de log.
    sys.stdout = Logger(ARQUIVO_DE_LOG)
    
    print("Iniciando execução do script...")
    print(f"Data e Hora: {datetime.datetime.now()}")
    print("-" * 30)
    
    main() # Executa a função principal
    
    print("-" * 30)
    print("Execução finalizada.")
