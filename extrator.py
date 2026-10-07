import re
import sqlite3
import requests
from bs4 import BeautifulSoup

conn = sqlite3.connect('dados/escalacoes.db')

# Garante que a coluna existe
try:
    conn.execute("ALTER TABLE noticias ADD COLUMN escalacao TEXT")
    conn.commit()
    print("Coluna 'escalacao' criada")
except sqlite3.OperationalError:
    print("Coluna 'escalacao' já existe")

# Palavras-gatilho que indicam escalação
GATILHOS = [
    r"prov[áa]vel escalação",
    r"provável time",
    r"escalação prov[áa]vel",
    r"time prov[áa]vel",
    r"deve (ir|escalar|entrar) (com|com o time)",
]

# Regex pra pegar sequência de nomes próprios separados por ; ou ,
# Ex: "João; Pedro, Lucas; Rafael, Bruno"
PADRAO_NOMES = re.compile(
    r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)?"
    r"(?:\s*[;,]\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)?){5,})"
)

def buscar_conteudo(url):
    """Baixa o conteúdo da notícia."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; EscalacoesBot/1.0)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Remove scripts e estilos
        for tag in soup(["script", "style"]):
            tag.decompose()
        texto = soup.get_text(" ", strip=True)
        return texto
    except Exception as e:
        return ""

def extrair_escalacao(texto):
    """Procura padrão de escalação no texto."""
    if not texto:
        return None
    
    # Normaliza espaços
    texto = re.sub(r"\s+", " ", texto)
    
    # Procura por gatilho
    for gatilho in GATILHOS:
        match = re.search(gatilho, texto, re.IGNORECASE)
        if match:
            # Pega 500 chars depois do gatilho
            trecho = texto[match.start():match.start() + 500]
            # Procura nomes
            nomes = PADRAO_NOMES.search(trecho)
            if nomes:
                seq = nomes.group(0)
                # Limpa e divide em nomes individuais
                lista = re.split(r"\s*[;,]\s*", seq)
                if len(lista) >= 8:  # pelo menos uns 8 nomes
                    return " | ".join(lista[:11])
    return None

# Pega as 5 notícias mais recentes de cada time que ainda não têm escalação
times = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
    "Botafogo", "Fluminense", "Vasco", "Grêmio",
    "Internacional", "Cruzeiro", "Atlético Mineiro", "Bahia",
    "Vitória", "Fortaleza", "Ceará", "Sport",
    "Juventude", "Bragantino", "Mirassol", "Santos"]

print("\n🔍 Procurando escalações nas notícias...\n")

total_extraidas = 0
for time in times:
    noticias = conn.execute(
        "SELECT id, link, titulo FROM noticias WHERE time=? AND (escalacao IS NULL OR escalacao='') ORDER BY coletado_em DESC LIMIT 3",
        (time,)
    ).fetchall()
    
    for id_not, link, titulo in noticias:
        conteudo = buscar_conteudo(link)
        escalacao = extrair_escalacao(conteudo)
        if escalacao:
            conn.execute("UPDATE noticias SET escalacao=? WHERE id=?", (escalacao, id_not))
            conn.commit()
            total_extraidas += 1
            print(f"✅ {time}: {escalacao[:60]}...")
            break  # achou 1, passa pro próximo time

print(f"\n📊 Total: {total_extraidas} escalações extraídas")
