import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

FOOTBALL_DATA_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "")

def obter_rodada_e_jogos():
    """Busca a rodada atual e os jogos do Brasileirão via API."""
    if not FOOTBALL_DATA_TOKEN:
        print("AVISO: Token da API não configurado. Usando dados manuais.")
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
        if match.get("status") in ("SCHEDULED", "TIMED", "IN_PLAY", "PAUSED"):
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
            try:
                dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
                dt_br = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
                dia_hora = dt_br.strftime("%d/%m %H:%M")
            except:
                dia_hora = "A definir"
        else:
            dia_hora = "A definir"
        
        jogos.append((casa, visitante, dia_hora))
    
    # Ordena por data
    jogos.sort(key=lambda x: x[2])
    
    # Formata a data da rodada (primeiro e último dia)
    data_rodada = ""
    if jogos:
        datas = [j[2].split()[0] for j in jogos if j[2] != "A definir"]
        if datas:
            if datas[0] == datas[-1]:
                data_rodada = datas[0]
            else:
                data_rodada = f"{datas[0]} a {datas[-1]}"
    
    print(f"Rodada {rodada_atual} obtida da API com {len(jogos)} jogos")
    return rodada_atual, data_rodada, jogos
