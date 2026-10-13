import requests
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

API_PONTUADOS = "https://api.cartolafc.globo.com/atletas/pontuados"
API_PARTIDAS = "https://api.cartolafc.globo.com/partidas"

ARQUIVO_ATUAL = "parciais.json"
ARQUIVO_ANTERIOR = "parciais_anterior.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def buscar_dados():
    resultado = {
        "ts": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
        "rodada": None,
        "atletas": {},
        "partidas": [],
    }
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
    if os.path.exists(ARQUIVO_ANTERIOR):
        with open(ARQUIVO_ANTERIOR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"atletas": {}}


def salvar_json(dados, arquivo):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def enviar_telegram(mensagem):
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
    """Formata TODOS os eventos detectados (sem filtro de scouts)."""
    if not eventos:
        return None

    linhas = [f"⚽ <b>Parciais Cartola</b> — {len(eventos)} mudanças\n"]
    for ev in eventos[:50]:  # Limita a 50 pra não estourar
        scouts_txt = " ".join(f"[{k}+{v}]" for k, v in ev["scouts"].items()) if ev["scouts"] else ""
        linhas.append(f"• <b>{ev['apelido']}</b>: +{ev['delta']:.1f} pts {scouts_txt}")

    if len(eventos) > 50:
        linhas.append(f"\n<i>... e mais {len(eventos) - 50} mudanças</i>")

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
        # Ordena por delta (maior primeiro)
        eventos.sort(key=lambda e: e["delta"], reverse=True)
        msg = formatar_eventos(eventos)
        if msg:
            enviar_telegram(msg)
            print(f"Telegram: {len(eventos)} mudanças notificadas")


if __name__ == "__main__":
    main()
