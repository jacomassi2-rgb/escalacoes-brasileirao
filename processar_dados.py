import pandas as pd
import json
import os

ARQUIVO_CSV = 'fathur_dados.csv'
ARQUIVO_JSON = 'dados.json'

if not os.path.exists(ARQUIVO_CSV):
    print("ERRO: fathur_dados.csv não encontrado")
    exit()

try:
    df = pd.read_csv(ARQUIVO_CSV)
    df = df.fillna(0)
    
    # Colunas que o Data Explorer vai usar
    colunas = [
        'apelido', 'clube_abrev', 'posicao_abrev', 'preco_num', 
        'score_contextualizado', 'score_teto', 'score_piso', 
        'perfil', 'status', 'adversario_abrev', 
        'mando', 'conquistado_media', 'cedido_media',
        'prob_vitoria', 'favoritismo', 'estilo_adversario'
    ]
    
    # Verifica quais colunas existem no CSV para evitar erros
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_filtrado = df[colunas_existentes]
    
    # Converte para dicionário (formato JSON)
    dados = df_filtrado.to_dict(orient='records')
    
    # Substitui valores NaN por 0 (para não quebrar o JavaScript)
    for j in dados:
        for k, v in j.items():
            if pd.isna(v):
                j[k] = 0
    
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False)
        
    print(f"Arquivo {ARQUIVO_JSON} gerado com sucesso! ({len(dados)} jogadores)")
    
except Exception as e:
    print(f"ERRO ao processar dados: {e}")
