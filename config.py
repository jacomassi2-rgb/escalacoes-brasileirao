# ==============================================
# CONFIGURAÇÕES DO SITE
# ==============================================
# Busca rodada, jogos e classificação via API
# Fallback pra dados manuais se API falhar
# ==============================================

import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FOOTBALL_DATA_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "")

# Fallback — usado se a API falhar ou não estiver configurada
RODADA_FALLBACK = 29
DATA_FALLBACK = "08 e 09 de outubro de 2026"
JOGOS_FALLBACK = [
    ("Internacional", "Corinthians", "08/10 19:00"),
    ("Remo", "Grêmio", "08/10 18:00"),
    ("Bragantino", "Mirassol", "08/10 20:30"),
    ("Vitória", "Chapecoense", "08/10 16:00"),
    ("Botafogo", "Vasco", "08/10 21:30"),
    ("Cruzeiro", "São Paulo", "08/10 17:00"),
    ("Santos", "Flamengo", "08/10 21:30"),
    ("Athletico Paranaense", "Atlético Mineiro", "08/10 18:30"),
    ("Palmeiras", "Bahia", "08/10 19:00"),
    ("Fluminense", "Coritiba", "08/10 20:00"),
]

CLASSIFICACAO_FALLBACK = []  # Preenchida automaticamente quando a API funciona


def _headers():
    return {"X-Auth-Token": FOOTBALL_DATA_TOKEN}


def _buscar_api():
    """Consulta a API do football-data.org (partidas)."""
    if not FOOTBALL_DATA_TOKEN:
        print("⚠️  FOOTBALL_DATA_TOKEN não configurado. Usando fallback.")
        return None
    
    url = "https://api.football-data.org/v4/competitions/BSA/matches"
    params = {"season": 2026}
    
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=10)
        if r.status_code != 200:
            print(f"⚠️  API matches retornou {r.status_code}. Usando fallback.")
            return None
        return r.json()
    except Exception as e:
        print(f"⚠️  Erro API matches: {e}. Usando fallback.")
        return None


def _buscar_classificacao():
    """Consulta a classificação atual do Brasileirão."""
    if not FOOTBALL_DATA_TOKEN:
        return None
    
    url = "https://api.football-data.org/v4/competitions/BSA/standings"
    params = {"season": 2026}
    
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=10)
        if r.status_code != 200:
            print(f"⚠️  API standings retornou {r.status_code}")
            return None
        data = r.json()
    except Exception as e:
        print(f"⚠️  Erro API standings: {e}")
        return None
    
    try:
        tabela = data["standings"][0]["table"]
        resultado = []
        for t in tabela:
            time_nome = t["team"].get("shortName") or t["team"]["name"]
            resultado.append({
                "posicao": t["position"],
                "time": time_nome,
                "pontos": t["points"],
                "jogos": t["playedGames"],
                "vitorias": t["won"],
                "empates": t["draw"],
                "derrotas": t["lost"],
                "gols_pro": t["goalsFor"],
                "gols_contra": t["goalsAgainst"],
                "saldo": t["goalDifference"],
            })
        return resultado
    except Exception as e:
        print(f"⚠️  Erro ao processar standings: {e}")
        return None


def _encontrar_rodada_atual(matches):
    """Encontra a rodada mais relevante (ao vivo > próxima > recente)."""
    agora = datetime.now(ZoneInfo("UTC"))
    limite_futuro = agora + timedelta(days=7)
    limite_passado = agora - timedelta(days=3)
    
    for m in matches:
        if m.get("status") in ("IN_PLAY", "PAUSED"):
            return m.get("matchday")
    
    rodadas_futuras = set()
    for m in matches:
        if m.get("status") in ("SCHEDULED", "TIMED"):
            utc = m.get("utcDate", "")
            if utc:
                try:
                    dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
                    if agora <= dt <= limite_futuro:
                        rodadas_futuras.add(m.get("matchday"))
                except:
                    pass
    if rodadas_futuras:
        return min(rodadas_futuras)
    
    rodadas_passadas = set()
    for m in matches:
        if m.get("status") == "FINISHED":
            utc = m.get("utcDate", "")
            if utc:
                try:
                    dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
                    if limite_passado <= dt <= agora:
                        rodadas_passadas.add(m.get("matchday"))
                except:
                    pass
    if rodadas_passadas:
        return max(rodadas_passadas)
    
    return None


def _formatar_jogo(match):
    """Extrai (casa, visitante, 'DD/MM HH:MM') de um match da API."""
    casa = match["homeTeam"].get("shortName") or match["homeTeam"]["name"]
    vis = match["awayTeam"].get("shortName") or match["awayTeam"]["name"]
    utc = match.get("utcDate", "")
    if utc:
        try:
            dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
            dt_br = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
            dia_hora = dt_br.strftime("%d/%m %H:%M")
        except:
            dia_hora = "A definir"
    else:
        dia_hora = "A definir"
    return (casa, vis, dia_hora)


def obter_rodada_e_jogos():
    """Retorna (rodada, data_rodada, jogos)."""
    data = _buscar_api()
    
    if data is None:
        print(f"📦 Usando fallback: Rodada {RODADA_FALLBACK}")
        return RODADA_FALLBACK, DATA_FALLBACK, JOGOS_FALLBACK
    
    matches = data.get("matches", [])
    if not matches:
        print(f"📦 API sem partidas. Usando fallback: Rodada {RODADA_FALLBACK}")
        return RODADA_FALLBACK, DATA_FALLBACK, JOGOS_FALLBACK
    
    rodada = _encontrar_rodada_atual(matches)
    if rodada is None:
        print(f"📦 Rodada não detectada. Usando fallback: {RODADA_FALLBACK}")
        return RODADA_FALLBACK, DATA_FALLBACK, JOGOS_FALLBACK
    
    jogos = []
    for m in matches:
        if m.get("matchday") == rodada:
            jogos.append(_formatar_jogo(m))
    
    jogos.sort(key=lambda x: x[2])
    
    datas = [j[2].split()[0] for j in jogos if j[2] != "A definir"]
    if datas:
        data_rodada = datas[0] if datas[0] == datas[-1] else f"{datas[0]} a {datas[-1]}"
    else:
        data_rodada = ""
    
    print(f"✅ API OK: Rodada {rodada} com {len(jogos)} jogos ({data_rodada})")
    return rodada, data_rodada, jogos


def obter_classificacao():
    """Retorna lista de dicts com a classificação atual."""
    data = _buscar_classificacao()
    if data is None:
        print("📦 Classificação via fallback (vazia)")
        return CLASSIFICACAO_FALLBACK
    
    print(f"✅ Classificação OK: {len(data)} times")
    return data
