import requests
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# ===== CONFIGURAÇÃO =====
API_PONTUADOS = "https://api.cartolafc.globo.com/atletas/pontuados"
API_PARTIDAS = "https://api.cartolafc.globo.com/partidas"

ARQUIVO_ATUAL = "parciais.json"
ARQUIVO_ANTERIOR = "parciais_anterior.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Scouts que disparam notificação imediata
SCOUTS_HOT = ["G", "A", "SG", "DP", "FT", "GC", "CV", "PS", "PP", "DE", "DS"]


def buscar_dados():
    """Busca pontuações e partidas da API do Cartola."""
    resultado = {
        "ts": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
        "rodada": None,
        "atletas": {},
        "partidas": [],
    }

    # 1. Todos os atletas que já pontuaram
    try:
        r = requests.get(API_PONTUADOS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            resultado["atletas"] = data.get("atletas", {})
            resultado["rodada"] = data.get("rodada")
        else:
            print(f"AVISO: /atletas/pontuados retornou {r.status_code}")
    except Exception as e:
        print(f"ERRO ao buscar pontuados: {e}")

    # 2. Partidas da rodada (com placar e clubes)
    try:
        r2 = requests.get(API_PARTIDAS, timeout=15)
        if r2.status_code == 200:
            data2 = r2.json()
            resultado["partidas"] = data2.get("partidas", [])
        else:
            print(f"AVISO: /partidas retornou {r2.status_code}")
    except Exception as e:
        print(f"ERRO ao buscar partidas: {e}")

    return resultado


def carregar_anterior():
    """Carrega o estado da execução anterior."""
    if os.path.exists(ARQUIVO_ANTERIOR):
        with open(ARQUIVO_ANTERIOR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"atletas": {}}


def salvar_json(dados, arquivo):
    """Salva dados em JSON."""
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def enviar_telegram(mensagem):
    """Envia notificação no Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"ERRO Telegram: {e}")


def formatar_eventos(eventos):
    """Formata lista de eventos para o Telegram."""
    if not eventos:
        return None

    # Filtra apenas eventos relevantes
    relevantes = []
    for ev in eventos:
        scouts = ev.get("scouts", {})
        if any(k in scouts for k in SCOUTS_HOT) or ev["delta"] >= 2.0:
            relevantes.append(ev)

    if not relevantes:
        return None

    linhas = [f"⚽ <b>Parciais Cartola</b> — {len(relevantes)} eventos\n"]
    for ev in relevantes[:20]:
        scouts_txt = " ".join(f"[{k}+{v}]" for k, v in ev["scouts"].items()) if ev["scouts"] else ""
        linhas.append(f"• <b>{ev['apelido']}</b>: +{ev['delta']:.1f} pts {scouts_txt}")
    return "\n".join(linhas)


def main():
    dados = buscar_dados()

    if not dados["atletas"]:
        print("Nenhum atleta pontuou ainda.")
        return

    anterior = carregar_anterior()
    atletas_antigos = anterior.get("atletas", {})

    eventos = []
    for atleta_id, info in dados["atletas"].items():
        apelido = info.get("apelido", "?")
        pontos = info.get("pontuacao", 0) or 0
        scout = info.get("scout", {}) or {}

        antigo = atletas_antigos.get(atleta_id, {})
        pontos_antigos = antigo.get("pontuacao", 0) or 0
        scout_antigo = antigo.get("scout", {}) or {}

        if pontos > pontos_antigos:
            scouts_novos = {
                k: v - (scout_antigo.get(k, 0) or 0)
                for k, v in scout.items()
                if v > (scout_antigo.get(k, 0) or 0)
            }
            eventos.append({
                "apelido": apelido,
                "delta": round(pontos - pontos_antigos, 1),
                "scouts": scouts_novos,
            })

    salvar_json(dados, ARQUIVO_ATUAL)
    salvar_json(dados, ARQUIVO_ANTERIOR)

    print(f"Parciais salvas: {len(dados['atletas'])} atletas")

    if eventos:
        msg = formatar_eventos(eventos)
        if msg:
            enviar_telegram(msg)
            print(f"Telegram: {len(eventos)} eventos notificados")


if __name__ == "__main__":
    main()
