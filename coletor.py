import feedparser
import sqlite3
import os
from urllib.parse import quote
from datetime import datetime

os.makedirs('dados', exist_ok=True)

conn = sqlite3.connect('dados/escalacoes.db')
conn.execute("""
    CREATE TABLE IF NOT EXISTS noticias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        titulo TEXT,
        link TEXT UNIQUE,
        fonte TEXT,
        publicado_em TEXT,
        coletado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

TIMES = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
    "Botafogo", "Fluminense", "Vasco", "Grêmio",
    "Internacional", "Cruzeiro", "Atlético Mineiro", "Bahia",
    "Vitória", "Fortaleza", "Ceará", "Sport",
    "Juventude", "Bragantino", "Mirassol", "Santos"]

def buscar(time):
    termo = f"provável escalação {time}"
    url = f"https://news.google.com/rss/search?q={quote(termo)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(url)
    for entry in feed.entries[:8]:
        titulo = entry.title.rsplit(" - ", 1)[0] if " - " in entry.title else entry.title
        fonte = entry.title.rsplit(" - ", 1)[-1] if " - " in entry.title else ""
        try:
            conn.execute(
                "INSERT OR IGNORE INTO noticias (time, titulo, link, fonte, publicado_em) VALUES (?,?,?,?,?)",
                (time, titulo, entry.link, fonte, entry.get("published", str(datetime.now())))
            )
        except:
            pass
    conn.commit()

print("Iniciando coleta...")
for time in TIMES:
    buscar(time)
print("Coleta finalizada!")
