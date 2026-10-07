import sqlite3
import os
from datetime import datetime

os.makedirs('site', exist_ok=True)

conn = sqlite3.connect('dados/escalacoes.db')

TIMES = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
    "Botafogo", "Fluminense", "Vasco", "Grêmio",
    "Internacional", "Cruzeiro", "Atlético Mineiro", "Bahia",
    "Vitória", "Fortaleza", "Ceará", "Sport",
    "Juventude", "Bragantino", "Mirassol", "Santos"]

html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Prováveis Escalações - Brasileirão</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background: #f5f5f5; }
  h1 { color: #0a5c2e; }
  .time { background: #fff; border-radius: 8px; padding: 1rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
  .time h2 { margin: 0 0 .5rem; font-size: 1.1rem; color: #0a5c2e; }
  .noticia { border-top: 1px solid #eee; padding: .5rem 0; }
  .noticia a { color: #1a4d8f; text-decoration: none; }
  .meta { font-size: .8rem; color: #888; }
</style>
</head>
<body>
<h1>⚽ Prováveis Escalações - Brasileirão Série A</h1>
<p>Atualizado em ATUALIZADO_AQUI</p>
CONTEUDO_AQUI
</body>
</html>"""

corpo = ""
for time in TIMES:
    linhas = conn.execute(
        "SELECT titulo, link, fonte FROM noticias WHERE time=? ORDER BY coletado_em DESC LIMIT 5",
        (time,)
    ).fetchall()
    corpo += f'<div class="time"><h2>{time}</h2>'
    if linhas:
        for titulo, link, fonte in linhas:
            corpo += f'<div class="noticia"><a href="{link}" target="_blank">{titulo}</a><div class="meta">{fonte}</div></div>'
    else:
        corpo += '<p>Nenhuma notícia encontrada.</p>'
    corpo += '</div>'

html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)

with open('site/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Site gerado com sucesso!")
