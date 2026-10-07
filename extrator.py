import re
import sqlite3
import requests
from bs4 import BeautifulSoup

conn = sqlite3.connect('dados/escalacoes.db')

# Garante coluna
try:
    conn.execute("ALTER TABLE noticias ADD COLUMN escalacao TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

# Palavras-gatilho (mais abrangentes)
GATILHOS = [
    r"prov[áa]ve(l|is) (escala[çc][ãa]o|time)",
    r"escala[çc][ãa]o (prov[áa]vel|do|para)",
    r"time (prov[áa]vel|deve)",
    r"deve (ir|escalar|entrar|come[çc]ar)",
    r"deve ser escalado",
    r"t[ée]cnico .{0,30}(escala|manda|coloca)",
]

# Regex que aceita nomes próprios (simples ou compostos)
NOME = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+(?:da|de|do|dos|das)?\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)?"
# Separadores: ; , e " e "
SEP = r"\s*(?:;|,|\se\s)\s*"

# Sequência de 5+ nomes (aceita ponto e vírgula, vírgula, "e")
PADRAO_NOMES = re.compile(
    NOME + r"(?:" + SEP + NOME + r"){4,}",
)

def buscar_conteudo(url):
    """Tenta extrair conteúdo real, seguindo redirects do Google News."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        texto = soup.get_text(" ", strip=True)
        return texto
    except Exception as e:
        return ""

def extrair_escalacao(texto):
    """Procura por padrão de escalação em qualquer lugar do texto."""
    if not texto:
        return None
    
    texto = re.sub(r"\s+", " ", texto)
    
    # Estratégia 1: procurar gatilho e pegar o trecho depois
    for gatilho in GATILHOS:
        for match in re.finditer(gatilho, texto, re.IGNORECASE):
            trecho = texto[match.start():match.start() + 600]
            nomes = PADRAO_NOMES.search(trecho)
            if nomes:
                seq = nomes.group(0)
                lista = re.split(SEP, seq)
                lista = [n.strip() for n in lista if n.strip()]
                if len(lista) >= 5:
                    return " | ".join(lista[:11])
    
    # Estratégia 2 (fallback): procurar QUALQUER sequência grande de nomes
    # Pode pegar escalação sem gatilho explícito
    todas = PADRAO_NOMES.findall(texto)
    if todas:
        seq = todas[0]
        lista = re.split(SEP, seq)
        lista = [n.strip() for n in lista if n.strip()]
        # Filtra nomes muito longos (provavelmente não são jogadores)
        lista = [n for n in lista if 3 <= len(n) <= 30]
        if len(lista) >= 7:
            return " | ".join(lista[:11])
    
    return None

times = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
    "Botafogo", "Fluminense", "Vasco", "Grêmio",
    "Internacional", "Cruzeiro", "Atlético Mineiro", "Bahia",
    "Vitória", "Fortaleza", "Ceará", "Sport",
    "Juventude", "Bragantino", "Mirassol", "Santos"]

print("\n🔍 Procurando escalações nas notícias...\n")

total_extraidas = 0
for time in times:
    noticias = conn.execute(
        "SELECT id, link, titulo FROM noticias WHERE time=? ORDER BY coletado_em DESC LIMIT 5",
        (time,)
    ).fetchall()
    
    achou = False
    for id_not, link, titulo in noticias:
        conteudo = buscar_conteudo(link)
        escalacao = extrair_escalacao(conteudo)
        if escalacao:
            conn.execute("UPDATE noticias SET escalacao=? WHERE id=?", (escalacao, id_not))
            conn.commit()
            total_extraidas += 1
            print(f"✅ {time}: {escalacao[:80]}...")
            achou = True
            break
    
    if not achou:
        print(f"❌ {time}: nenhuma escalação encontrada")

print(f"\n📊 Total: {total_extraidas} escalações extraídas")
