import os
import requests
from datetime import datetime

FOOTBALL_DATA_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "")

def obter_rodada_e_jogos():
    """Busca a rodada atual e os jogos do Brasileirão via API."""
    if not FOOTBALL_DATA_TOKEN:
        # Se não tiver token, usa dados de fallback
        return 29, "07 e 08 de outubro de 2026", []
    
    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    url = "https://api.football-data.org/v4/competitions/BSA/matches"
    params = {"season": 2026}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return 29, "07 e 08 de outubro de 2026", []
    
    # Encontra a rodada mais recente com jogos agendados ou em andamento
    rodada_atual = 1
    for match in data.get("matches", []):
        md = match.get("matchday", 1)
        if match.get("status") in ("SCHEDULED", "TIMED", "IN_PLAY"):
            if md > rodada_atual:
                rodada_atual = md
    
    # Pega os jogos dessa rodada
    jogos = []
    for match in data.get("matches", []):
        if match.get("matchday") != rodada_atual:
            continue
        casa = match["homeTeam"].get("shortName") or match["homeTeam"]["name"]
        visitante = match["awayTeam"].get("shortName") or match["awayTeam"]["name"]
        utc_date = match.get("utcDate", "")
        
        if utc_date:
            dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
            # Converte pra horário de Brasília
            from zoneinfo import ZoneInfo
            dt_br = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
            dia_hora = dt_br.strftime("%d/%m %H:%M")
        else:
            dia_hora = "A definir"
        
        jogos.append((casa, visitante, dia_hora))
    
    # Ordena por data
    jogos.sort(key=lambda x: x[2])
    
    return rodada_atual, "", jogos
