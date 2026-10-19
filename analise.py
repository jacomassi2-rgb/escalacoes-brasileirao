import pandas as pd
import json
import os

# Carrega o CSV do Fathur
if not os.path.exists('fathur_dados.csv'):
    print("ERRO: fathur_dados.csv não encontrado")
    exit()

df = pd.read_csv('fathur_dados.csv')

# Limpa dados nulos
df = df.dropna(subset=['apelido', 'score_contextualizado', 'preco_num'])
df = df[df['preco_num'] > 0]

# Calcula o PPM (Pontos por Milhão)
df['ppm'] = (df['score_contextualizado'] / df['preco_num']) * 10

# 1. Top 10 Custo-Benefício (PPM)
top_ppm = df.sort_values('ppm', ascending=False).head(10)

# 2. Alerta de Armadilha (Score alto, mas risco alto)
# Consideramos "armadilha" se o score for > 5.0 e o perfil for Volátil ou Piso negativo
armadilhas = df[
    (df['score_contextualizado'] >= 5.0) & 
    ((df['perfil'] == 'Volatil') | (df['score_piso'] < 0))
].sort_values('score_contextualizado', ascending=False).head(5)

# 3. O time do usuário (para comparação)
meu_time = []
if os.path.exists('meu_time.json'):
    with open('meu_time.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        meu_time = [j['nome'].lower() for j in data.get('jogadores', [])]

# Gera o HTML do relatório
html = "<h2>📊 Relatório de Decisão</h2>"

html += "<h3>💰 Top 10 Custo-Benefício (PPM)</h3>"
html += "<table><tr><th>Jogador</th><th>Clube</th><th>Score</th><th>Preço</th><th>PPM</th></tr>"
for _, row in top_ppm.iterrows():
    is_meu = "⭐ " if row['apelido'].lower() in meu_time else ""
    html += f"<tr><td>{is_meu}{row['apelido']}</td><td>{row['clube_abrev']}</td><td>{row['score_contextualizado']:.1f}</td><td>R$ {row['preco_num']:.2f}</td><td><b>{row['ppm']:.2f}</b></td></tr>"
html += "</table>"

html += "<h3>⚠️ Alerta de Armadilha (Alto Score, Alto Risco)</h3>"
html += "<table><tr><th>Jogador</th><th>Clube</th><th>Score</th><th>Piso</th><th>Perfil</th></tr>"
for _, row in armadilhas.iterrows():
    is_meu = "⭐ " if row['apelido'].lower() in meu_time else ""
    html += f"<tr><td>{is_meu}{row['apelido']}</td><td>{row['clube_abrev']}</td><td>{row['score_contextualizado']:.1f}</td><td>{row['score_piso']:.1f}</td><td>{row['perfil']}</td></tr>"
html += "</table>"

# Salva num arquivo para o gerar_site.py ler
with open('analise_relatorio.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Relatório de análise gerado com sucesso!")
