import asyncio
import json
import os
from twikit import Client

# Palavras-chave que indicam notícia relevante sobre escalação
PALAVRAS_CHAVE = [
    "escalação", "provavel", "provável", "dúvida", "duvida", "titular",
    "lesão", "lesao", "suspenso", "poupado", "volta", "desfalque",
    "confirmado", "retorna", "fora"
]


async def main():
    # Carrega os cookies do secret
    cookies_str = os.environ.get("X_COOKIES", "")
    if not cookies_str:
        print("ERRO: X_COOKIES não configurado")
        return

    cookies = json.loads(cookies_str)
    print(f"Cookies carregados: {list(cookies.keys())}")

    # Carrega a lista de setoristas
    with open('setoristas.json', 'r', encoding='utf-8') as f:
        setoristas = json.load(f)

    todos_tweets = []

    # Inicializa o cliente com os cookies
    client = Client(language='pt-BR')
    client.set_cookies(cookies)

    for clube, handles in setoristas.items():
        print(f"Buscando setoristas do {clube}...")
        for handle in handles:
            print(f"  @{handle}")
            try:
                # Busca os 20 tweets mais recentes do perfil
                tweets = await client.get_user_tweets(handle, tweet_type='Tweets', count=20)
                encontrados = 0
                for tweet in tweets:
                    texto = tweet.text.lower()
                    if any(p in texto for p in PALAVRAS_CHAVE):
                        todos_tweets.append({
                            "clube": clube,
                            "setorista": handle,
                            "titulo": tweet.text,
                            "link": f"https://x.com/{handle}/status/{tweet.id}",
                            "data": str(tweet.created_at)
                        })
                        encontrados += 1
                print(f"     -> {encontrados} tweets relevantes de {len(tweets)} lidos")
            except Exception as e:
                print(f"     ERRO: {e}")
            await asyncio.sleep(2)  # Delay maior pra evitar bloqueio

    # Salva o resultado
    with open('noticias_setoristas.json', 'w', encoding='utf-8') as f:
        json.dump(todos_tweets, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(todos_tweets)} tweets salvos em noticias_setoristas.json")


if __name__ == "__main__":
    asyncio.run(main())
