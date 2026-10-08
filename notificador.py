import os
import json
import requests
import sqlite3
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
from config import obter_rodada_e_jogos, obter_classificacao


def normalizar(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def buscar_alertas(jogadores):
    """Busca alertas nas notícias pra cada jogador do time."""
    if not os.path.exists('dados/escalacoes.db'):
        return []
    
    conn = sqlite3.connect('dados/escalacoes.db')
    
    negativas = ["lesão", "lesao", "lesionado", "dúvida", "duvida",
                 "suspenso", "suspensao", "suspensão", "cortado", "fora",
                 "poupado", "poupanca", "poupança", "não joga", "nao joga",
                 "desfalque", "contundido", "machucado", "departamento médico"]
    
    positivas = ["confirmado", "titular", "retorna", "volta", "escalado",
                 "à disposição", "a disposicao", "disponível", "disponivel",
                 "recuperado", "pronto", "joga"]
    
    alertas = []
    for j in jogadores:
        nome = j.get("nome", "")
        nome_norm = normalizar(nome)
        if len(nome_norm) < 3:
            continue
        
        try:
            linhas = conn.execute(
                "SELECT titulo, link, fonte FROM noticias WHERE lower(titulo) LIKE ? ORDER BY coletado_em DESC LIMIT 5",
                (f"%{nome_norm}%",)
            ).fetchall()
        except:
            continue
        
        for titulo, link, fonte in linhas:
            titulo_norm = normalizar(titulo)
            if nome_norm not in titulo_norm:
                continue
            
            tem_neg = any(p in titulo_norm for p in negativas)
            tem_pos = any(p in titulo_norm for p in positivas)
            
            if tem_neg:
                alertas.append({"tipo": "negativo", "nome": nome, "titulo": titulo, "fonte": fonte})
                break
            elif tem_pos:
                alertas.append({"tipo": "positivo", "nome": nome, "titulo": titulo, "fonte": fonte})
                break
    
    conn.close()
    return alertas


def gerar_mensagem():
    """Gera a mensagem completa do dia."""
    rodada, data_rodada, jogos = obter_rodada_e_jogos()
    classificacao = obter_classificacao()
    hora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    
    linhas = []
    linhas.append(f"🤖 <b>Fathur FC</b> — Rodada {rodada}")
    linhas.append("")
    
    if data_rodada:
        linhas.append(f"📅 {data_rodada}")
    linhas.append(f"⏰ Atualizado: {hora}")
    linhas.append("")
    
    # Jogos do dia (máximo 3)
    if jogos:
        linhas.append("⚽ <b>Jogos da rodada:</b>")
        jogos_hoje = [j for j in jogos if len(j) == 3]
        for casa, vis, dia_hora in jogos_hoje[:3]:
            linhas.append(f"• {casa} x {vis} — {dia_hora}")
        if len(jogos_hoje) > 3:
            linhas.append(f"<i>...e mais {len(jogos_hoje) - 3} jogos</i>")
        linhas.append("")
    
    # Meu Time + Alertas
    if os.path.exists('meu_time.json'):
        try:
            with open('meu_time.json', 'r', encoding='utf-8') as f:
                meu_time = json.load(f)
            jogadores = meu_time.get("jogadores", [])
            
            if jogadores:
                linhas.append(f"📊 <b>Seu time:</b> {len(jogadores)} jogadores")
                
                # Acordo com Fathur
                if os.path.exists('sugestao_fathur.json'):
                    try:
                        with open('sugestao_fathur.json', 'r', encoding='utf-8') as f:
                            sugestao = json.load(f)
                        nomes_fathur = {normalizar(j["nome"]) for j in sugestao.get("jogadores", [])}
                        acertos = sum(1 for j in jogadores if normalizar(j.get("nome", "")) in nomes_fathur)
                        if jogadores:
                            pct = acertos / len(jogadores) * 100
                            linhas.append(f"⚔️ Acordo Fathur: {acertos}/{len(jogadores)} ({pct:.0f}%)")
                    except:
                        pass
                linhas.append("")
                
                # Alertas
                alertas = buscar_alertas(jogadores)
                if alertas:
                    linhas.append(f"🔔 <b>Alertas ({len(alertas)}):</b>")
                    for a in alertas[:5]:
                        icone = "🔴" if a["tipo"] == "negativo" else "🟢"
                        titulo_curto = a["titulo"][:60] + "..." if len(a["titulo"]) > 60 else a["titulo"]
                        linhas.append(f"{icone} <b>{a['nome']}</b> — {titulo_curto}")
                    linhas.append("")
        except Exception as e:
            print(f"Erro lendo meu_time: {e}")
    
    # Classificação (top 3)
    if classificacao and len(classificacao) >= 3:
        linhas.append("🏆 <b>Top 3 do Brasileirão:</b>")
        for i, t in enumerate(classificacao[:3], 1):
            linhas.append(f"{i}º {t['time']} — {t['pontos']}pts")
        linhas.append("")
    
    # Rodapé
    linhas.append("🔗 jacomassi2-rgb.github.io/escalacoes-brasileirao")
    
    return "\n".join(linhas)


def enviar():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurado")
        return
    
    mensagem = gerar_mensagem()
    
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": mensagem,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true"
        }
    )
    
    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text[:200]}")


if __name__ == "__main__":
    enviar()
