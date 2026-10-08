# ==============================================
# CONFIGURAÇÕES DO SITE
# ==============================================
# Busca rodada e jogos automaticamente da API
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


def _buscar_api():
    """Consulta a API do football-data.org."""
    if not FOOTBALL_DATA_TOKEN:
        print("⚠️  FOOTBALL_DATA_TOKEN não configurado. Usando fallback.")
        return None
    
    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    url = "https://api.football-data.org/v4/competitions/BSA/matches"
    params = {"season": 2026}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            print(f"⚠️  API retornou {r.status_code}. Usando fallback.")
            return None
        return r.json()
    except Exception as e:
        print(f"⚠️  Erro ao consultar API: {e}. Usando fallback.")
        return None


def _encontrar_rodada_atual(matches):
    """Encontra a rodada mais relevante (ao vivo > próxima > recente)."""
    agora = datetime.now(ZoneInfo("UTC"))
    limite_futuro = agora + timedelta(days=7)
    limite_passado = agora - timedelta(days=3)
    
    # Prioridade 1: jogos AO VIVO
    for m in matches:
        if m.get("status") in ("IN_PLAY", "PAUSED"):
            return m.get("matchday")
    
    # Prioridade 2: próximos 7 dias
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
    
    # Prioridade 3: últimos 3 dias
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
    """
    Retorna (rodada, data_rodada, jogos).
    Tenta API primeiro; se falhar, usa fallback.
    """
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
        print(f"📦 Não consegui detectar rodada. Usando fallback: {RODADA_FALLBACK}")
        return RODADA_FALLBACK, DATA_FALLBACK, JOGOS_FALLBACK
    
    # Pega os jogos dessa rodada
    jogos = []
    for m in matches:
        if m.get("matchday") == rodada:
            jogos.append(_formatar_jogo(m))
    
    jogos.sort(key=lambda x: x[2])
    
    # Data da rodada (primeiro ao último dia)
    datas = [j[2].split()[0] for j in jogos if j[2] != "A definir"]
    if datas:
        data_rodada = datas[0] if datas[0] == datas[-1] else f"{datas[0]} a {datas[-1]}"
    else:
        data_rodada = ""
    
    print(f"✅ API OK: Rodada {rodada} com {len(jogos)} jogos ({data_rodada})")
    return rodada, data_rodada, jogos
