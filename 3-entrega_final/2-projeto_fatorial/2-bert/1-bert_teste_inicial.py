# -*- coding: utf-8 -*-
"""
Script de teste inicial para o BERT.

Objetivo: Verificar se o dataset, o tokenizador e o modelo pré-treinado
conseguem ser carregados corretamente no ambiente.
"""
# --------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# --------------------------------------------------------------------------
import pandas as pd
import os  # Importa a biblioteca 'os'
from transformers import BertTokenizer, BertForSequenceClassification

# --------------------------------------------------------------------------
# 2. CONFIGURAÇÕES GLOBAIS
# --------------------------------------------------------------------------
# --- Definição dinâmica do caminho do arquivo de dados ---
script_dir = os.path.dirname(os.path.abspath(__file__))
nome_arquivo_csv = 'amostra_rotulada.csv'
NOME_ARQUIVO_DADOS = os.path.join(script_dir, nome_arquivo_csv)

# --- Parâmetros do modelo ---
# Usamos o 'bert-base', que é mais leve e funcionou bem no nosso hardware.
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased'

# --------------------------------------------------------------------------
# 3. EXECUÇÃO DO TESTE
# --------------------------------------------------------------------------
def teste_inicial():
    """Executa os passos de verificação."""
    
    # 1. Carregar o dataset
    print("--- PASSO 1: Carregando o dataset ---")
    try:
        df = pd.read_csv(NOME_ARQUIVO_DADOS)
        print(f"Dataset '{os.path.basename(NOME_ARQUIVO_DADOS)}' carregado com sucesso!")
        print(f"Amostra dos dados:\n{df.head()}\n")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{os.path.basename(NOME_ARQUIVO_DADOS)}' não encontrado.")
        print(f"Certifique-se de que ele está na pasta: {script_dir}")
        return

    # 2. Carregar o Tokenizador
    print("--- PASSO 2: Carregando o tokenizador ---")
    try:
        tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT)
        print(f"Tokenizador do modelo '{NOME_MODELO_BERT}' carregado com sucesso!\n")
    except Exception as e:
        print(f"ERRO ao carregar o tokenizador: {e}")
        return

    # 3. Carregar o Modelo
    print("--- PASSO 3: Carregando o modelo pré-treinado ---")
    try:
        # Usamos 'BertForSequenceClassification' pois nossa tarefa final é de classificação.
        # 'num_labels=2' informa ao modelo que temos duas classes (Tóxico/Não Tóxico).
        model = BertForSequenceClassification.from_pretrained(NOME_MODELO_BERT, num_labels=2)
        print(f"Modelo '{NOME_MODELO_BERT}' carregado com sucesso!\n")
    except Exception as e:
        print(f"ERRO ao carregar o modelo: {e}")
        return

    # 4. Teste rápido de tokenização
    print("--- PASSO 4: Testando o tokenizador ---")
    exemplo_texto = "Isso é apenas um teste para o tokenizador."
    tokens = tokenizer.tokenize(exemplo_texto)
    print(f"Frase original: '{exemplo_texto}'")
    print(f"Frase tokenizada: {tokens}\n")
    
    print("--- Teste inicial concluído com sucesso! ---")

# --------------------------------------------------------------------------
# 4. PONTO DE ENTRADA DO SCRIPT
# --------------------------------------------------------------------------
if __name__ == '__main__':
    teste_inicial()