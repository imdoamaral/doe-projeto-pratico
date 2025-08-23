# -*- coding: utf-8 -*-
"""
Script para carregar o dataset rotulado, o modelo BERTimbau, seu tokenizador,
e preparar (tokenizar) os dados para o treinamento (fine-tuning).

Este script é um passo de verificação para garantir que a preparação dos dados
está funcionando como esperado antes de partir para o treinamento.
"""
# --------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# --------------------------------------------------------------------------
import pandas as pd
import torch
import os  # Importa a biblioteca 'os'
from transformers import BertTokenizer

# --------------------------------------------------------------------------
# 2. CONFIGURAÇÕES GLOBAIS
# --------------------------------------------------------------------------
# --- Definição dinâmica dos caminhos dos arquivos ---
script_dir = os.path.dirname(os.path.abspath(__file__))
nome_arquivo_csv = 'amostra_rotulada.csv'
NOME_ARQUIVO_DADOS = os.path.join(script_dir, nome_arquivo_csv)

# --- Parâmetros do modelo e colunas ---
NOME_COLUNA_TEXTO = 'mensagem'
NOME_COLUNA_ROTULO = 'classificacao_binaria'
NOME_MODELO_BERT = 'neuralmind/bert-base-portuguese-cased'

# --- Parâmetros da Tokenização ---
MAX_LENGTH = 128  # Comprimento máximo das sentenças

# --------------------------------------------------------------------------
# 3. FUNÇÃO PRINCIPAL
# --------------------------------------------------------------------------
def preparar_dados():
    """
    Função principal que executa todos os passos de carregamento e tokenização.
    """
    print("--- INÍCIO DA PREPARAÇÃO DOS DADOS PARA O BERT ---")

    # Carregar o dataset
    try:
        print(f"\n[PASSO 1/4] Carregando o dataset '{os.path.basename(NOME_ARQUIVO_DADOS)}'...")
        df = pd.read_csv(NOME_ARQUIVO_DADOS)
        print("Dataset carregado com sucesso!")
        print(f"O dataset tem {len(df)} linhas.")
    except FileNotFoundError:
        print(f"\nERRO: O arquivo de dados '{os.path.basename(NOME_ARQUIVO_DADOS)}' não foi encontrado.")
        print(f"Por favor, certifique-se de que ele está na mesma pasta que o script:")
        print(f"-> {script_dir}")
        return

    # Verificar se as colunas necessárias existem
    colunas_necessarias = [NOME_COLUNA_TEXTO, NOME_COLUNA_ROTULO]
    if not all(col in df.columns for col in colunas_necessarias):
        print("\nERRO: Uma ou mais colunas necessárias não foram encontradas no arquivo CSV.")
        print(f"Colunas esperadas: {colunas_necessarias}")
        print(f"Colunas encontradas: {df.columns.tolist()}")
        return

    # Carregar o Tokenizador
    print("\n[PASSO 2/4] Carregando o tokenizador do BERTimbau...")
    try:
        tokenizer = BertTokenizer.from_pretrained(NOME_MODELO_BERT)
        print("Tokenizador carregado com sucesso!")
    except Exception as e:
        print(f"ERRO ao carregar o tokenizador: {e}")
        return

    # Extrair textos e rótulos do DataFrame
    textos = df[NOME_COLUNA_TEXTO].astype(str).tolist()
    rotulos = df[NOME_COLUNA_ROTULO].tolist()

    # Tokenizar os dados
    print(f"\n[PASSO 3/4] Aplicando o tokenizador em {len(textos)} textos...")
    encoded_data = tokenizer.batch_encode_plus(
        textos,
        add_special_tokens=True,
        return_attention_mask=True,
        padding='max_length',
        max_length=MAX_LENGTH,
        truncation=True,
        return_tensors='pt'  # Retorna como Tensores do PyTorch
    )

    input_ids = encoded_data['input_ids']
    attention_masks = encoded_data['attention_mask']
    labels = torch.tensor(rotulos)
    print("Tokenização completa!")

    # Verificação final
    print("\n[PASSO 4/4] Verificando os resultados...")
    print(f"Formato dos 'input_ids': {input_ids.shape}")
    print(f"Formato das 'attention_masks': {attention_masks.shape}")
    print(f"Formato dos 'labels': {labels.shape}")

    print("\n--- Exemplo da primeira frase processada ---")
    print(f"Texto Original: '{textos[0]}'")
    print(f"Texto decodificado do tensor: '{tokenizer.decode(input_ids[0], skip_special_tokens=True)}'")
    print(f"Label: {labels[0]}")

    print("\n--- PREPARAÇÃO CONCLUÍDA COM SUCESSO ---")


# --------------------------------------------------------------------------
# 4. PONTO DE ENTRADA DO SCRIPT
# --------------------------------------------------------------------------
if __name__ == '__main__':
    preparar_dados()