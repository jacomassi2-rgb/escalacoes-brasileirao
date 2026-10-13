import requests

MIRRORS = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.cz",
    "https://xcancel.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for base in MIRRORS:
    try:
        r = requests.get(f"{base}/elonmusk/rss", headers=HEADERS, timeout=8)
        print(f"{base} -> status {r.status_code} | tamanho {len(r.text)}")
    except Exception as e:
        print(f"{base} -> ERRO: {e}")
