import requests
import json
import os
import time
from bs4 import BeautifulSoup

# Só o mirror que funciona (descoberto via teste)
NITTER_MIRRORS = [
    "https://nitter.cz",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

PALAVRAS_CHAVE = [
    "escalação", "provavel", "provável", "dúvida", "duvida", "titular",
    "lesão", "lesao", "suspenso", "poupado", "volta", "desfalque",
    "confirmado", "retorna", "fora"
]


def fetch_rss(handle):
    """Busca o RSS do perfil no Nitter."""
    for base in NITTER_MIRRORS:
        try:
            url = f"{base}/{handle}/rss"
            resp = requests.get(url, headers=HEADERS, timeout=5)
            if resp.status_code == 200 and "<rss" in resp.text:
                return resp.text
        except Exception as e:
            print(f"     ERRO: {e}")
            continue
    return None


def processar_tweets(xml_content, clube, handle):
    """Extrai títulos e links do XML do RSS."""
    tweets = []
    if not xml_content:
        return tweets

    soup = BeautifulSoup(xml_content, "xml")
    for item in soup.find_all("item"):
        titulo = item.title.text if item.title else ""
        link = item.link.text if item.link else ""
        pub_date = item.pubDate.text if item.pubDate else ""

        titulo_lower = titulo.lower()
        if any(p in titulo_lower for p in PALAVRAS_CHAVE):
            tweets.append({
                "clube": clube,
                "setorista": handle,
                "titulo": titulo,
                "link": link,
                "data": pub_date
            })
    return tweets


def main():
    with open('setoristas.json', 'r', encoding='utf-8') as f:
        setoristas = json.load(f)

    todos_tweets = []

    for clube, handles in setoristas.items():
        print(f"Buscando setoristas do {clube}...")
        for handle in handles:
            print(f"  {handle}")
            xml = fetch_rss(handle)
            tweets = processar_tweets(xml, clube, handle)
            todos_tweets.extend(tweets)
            print(f"     -> {len(tweets)} tweets relevantes")
            time.sleep(0.5)  # Delay pra não bloquear

    with open('noticias_setoristas.json', 'w', encoding='utf-8') as f:
        json.dump(todos_tweets, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(todos_tweets)} tweets salvos em noticias_setoristas.json")


if __name__ == "__main__":
    main()
