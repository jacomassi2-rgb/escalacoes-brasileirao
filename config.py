import os
import requests
from datetime import datetime, timedelta
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
    
    agora = datetime.now(ZoneInfo("UTC"))
    limite = agora + timedelta(days=7)  # Olha até 7 dias pra frente
    
    # Estratégia: encontrar a rodada com jogos mais próximos de agora
    # 1. Primeiro tenta achar jogos EM ANDAMENTO (IN_PLAY, PAUSED)
    # 2. Depois jogos AGENDADOS para os próximos 7 dias
    # 3. Por último, jogos FINALIZADOS recentemente (últimos 3 dias)
    
    rodada_atual = None
    
    # Prioridade 1: jogos ao vivo
    for match in data.get("matches", []):
        if match.get("status") in ("IN_PLAY", "PAUSED"):
            rodada_atual = match.get("matchday")
            break
    
    # Prioridade 2: jogos agendados nos próximos 7 dias
    if rodada_atual is None:
        for match in data.get("matches", []):
            if match.get("status") in ("SCHEDULED", "TIMED"):
                utc_date = match.get("utcDate", "")
                if utc_date:
                    try:
                        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
                        if agora <= dt <= limite:
                            md = match.get("matchday")
                            if rodada_atual is None or md < rodada_atual:
                                rodada_atual = md
                    except:
                        pass
    
    # Prioridade 3: jogos finalizados nos últimos 3 dias
    if rodada_atual is None:
        limite_passado = agora - timedelta(days=3)
        for match in data.get("matches", []):
            if match.get("status") == "FINISHED":
                utc_date = match.get("utcDate", "")
                if utc_date:
                    try:
                        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
                        if limite_passado <= dt <= agora:
                            md = match.get("matchday")
                            if rodada_atual is None or md > rodada_atual:
                                rodada_atual = md
                    except:
                        pass
    
    if rodada_atual is None:
        rodada_atual = 29  # Fallback
    
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
