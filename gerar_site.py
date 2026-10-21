import sqlite3
import json
import os
from datetime import datetime
from email.utils import parsedate_to_datetime
from config import obter_rodada_e_jogos, obter_classificacao

RODADA_ATUAL, DATA_RODADA, JOGOS_RODADA = obter_rodada_e_jogos()
CLASSIFICACAO = obter_classificacao()

conn = sqlite3.connect('dados/escalacoes.db')

TOKEN_LOGODEV = "pk_A_4R97saSLeUXjVT7UOFWg"

def logo(dominio):
    return f"https://img.logo.dev/{dominio}?token={TOKEN_LOGODEV}&size=80&retina=true"

TIMES = [
    ("Flamengo", logo("flamengo.com.br"), "#c8102e"),
    ("Palmeiras", logo("palmeiras.com.br"), "#006437"),
    ("Corinthians", logo("corinthians.com.br"), "#000000"),
    ("São Paulo", logo("saopaulofc.net"), "#e30613"),
    ("Botafogo", logo("botafogo.com.br"), "#000000"),
    ("Fluminense", logo("fluminense.com.br"), "#7a0d1d"),
    ("Vasco", logo("vasco.com.br"), "#000000"),
    ("Grêmio", logo("gremio.net"), "#0d47a1"),
    ("Internacional", logo("internacional.com.br"), "#c8102e"),
    ("Cruzeiro", logo("cruzeiro.com.br"), "#0d47a1"),
    ("Atlético Mineiro", logo("atletico.com.br"), "#000000"),
    ("Bahia", logo("esporteclubebahia.com.br"), "#003399"),
    ("Vitória", logo("ecvitoria.com.br"), "#c8102e"),
    ("Remo", logo("clubedoremo.com.br"), "#003366"),
    ("Chapecoense", logo("chapecoense.com.br"), "#006437"),
    ("Coritiba", logo("coritiba.com.br"), "#006437"),
    ("Athletico Paranaense", logo("athletico.com.br"), "#c8102e"),
    ("Bragantino", logo("redbullbragantino.com.br"), "#c8102e"),
    ("Mirassol", logo("mirassolfc.com.br"), "#006437"),
    ("Santos", logo("santosfc.com.br"), "#000000"),
]

def tempo_relativo(data_str):
    try:
        dt = parsedate_to_datetime(data_str)
        agora = datetime.now(dt.tzinfo)
        segundos = int((agora - dt).total_seconds())
        if segundos < 60: return "agora mesmo"
        elif segundos < 3600: return f"há {segundos // 60} min"
        elif segundos < 86400: return f"há {segundos // 3600} h"
        else: return f"há {segundos // 86400} dias"
    except: return ""

def tempo_em_horas(data_str):
    try:
        dt = parsedate_to_datetime(data_str)
        agora = datetime.now(dt.tzinfo)
        return (agora - dt).total_seconds() / 3600
    except: return 9999

MEU_TIME = {}
if os.path.exists('meu_time.json'):
    with open('meu_time.json', 'r', encoding='utf-8') as f:
        MEU_TIME = json.load(f)

SUGESTAO_FATHUR = {}
if os.path.exists('sugestao_fathur.json'):
    with open('sugestao_fathur.json', 'r', encoding='utf-8') as f:
        SUGESTAO_FATHUR = json.load(f)

# ============================================
# CALCULA PONTOS REAIS DO MEU TIME
# ============================================
PONTOS_REAIS = {}
if os.path.exists('parciais.json'):
    with open('parciais.json', 'r', encoding='utf-8') as f:
        parciais = json.load(f)
    for atleta_id, info in parciais.get('atletas', {}).items():
        apelido = info.get('apelido', '').lower().strip()
        PONTOS_REAIS[apelido] = info.get('pontuacao', 0) or 0

# Lê o template HTML (modelo.html)
with open('modelo.html', 'r', encoding='utf-8') as f:
    html = f.read()

if JOGOS_RODADA:
    jogos_html = "".join(
        f'<div class="jogo"><strong>{casa} x {vis}</strong>{dia}</div>'
        for casa, vis, dia in JOGOS_RODADA
    )
else:
    jogos_html = ""

corpo = ""
for nome, logo_url, cor in TIMES:
    linhas = conn.execute(
        "SELECT titulo, link, fonte, publicado_em FROM noticias WHERE time=? ORDER BY coletado_em DESC LIMIT 5",
        (nome,)
    ).fetchall()
    corpo += f'<div class="time" data-time="{nome}" style="border-left-color:{cor}">'
    if linhas:
        primeiro_link = linhas[0][1]
        qtd = len(linhas)
        corpo += f'''<div class="time-header">
            <img src="{logo_url}" alt="{nome}" onerror="this.style.display='none'">
            <h2>{nome}</h2>
            <span class="contador">{qtd} notícias</span>
            <a href="{primeiro_link}" target="_blank" class="btn-escalacao">🟢 Ver escalação</a>
        </div>'''
    else:
        corpo += f'''<div class="time-header">
            <img src="{logo_url}" alt="{nome}" onerror="this.style.display='none'">
            <h2>{nome}</h2>
        </div>'''
    if linhas:
        for titulo, link, fonte, publicado_em in linhas:
            tempo = tempo_relativo(publicado_em)
            horas = tempo_em_horas(publicado_em)
            meta = f'<span>{fonte}</span>'
            if tempo:
                meta += f'<span class="tempo">⏱ {tempo}</span>'
            corpo += f'<div class="noticia" data-horas="{horas:.1f}"><a href="{link}" target="_blank">{titulo}</a><div class="meta">{meta}</div></div>'
        corpo += '<div class="vazio vazio-24h oculto">Nenhuma notícia nas últimas 24 horas.</div>'
    else:
        corpo += '<div class="vazio">Nenhuma notícia encontrada.</div>'
    corpo += '</div>'

if CLASSIFICACAO:
    linhas_tabela = ""
    for t in CLASSIFICACAO:
        pos = t["posicao"]
        if pos <= 4: classe = "g4 libertadores"
        elif pos <= 8: classe = "g5-g8 pre-libertadores"
        elif pos <= 16: classe = "g9-g16"
        else: classe = "z4 rebaixamento"
        linhas_tabela += f'''<tr class="{classe}">
            <td><span class="pos">{pos}</span></td>
            <td><span class="time-nome">{t["time"]}</span></td>
            <td class="num"><b>{t["pontos"]}</b></td>
            <td class="num">{t["jogos"]}</td>
            <td class="num col-v-e-d">{t["vitorias"]}</td>
            <td class="num col-v-e-d">{t["empates"]}</td>
            <td class="num col-v-e-d">{t["derrotas"]}</td>
            <td class="num col-gp-gc">{t["gols_pro"]}</td>
            <td class="num col-gp-gc">{t["gols_contra"]}</td>
            <td class="num">{t["saldo"]:+d}</td>
        </tr>'''
    tabela_html = f'''<table class="classificacao">
        <thead>
            <tr>
                <th style="width:40px;">#</th>
                <th>Time</th>
                <th class="num">Pts</th>
                <th class="num">J</th>
                <th class="num col-v-e-d">V</th>
                <th class="num col-v-e-d">E</th>
                <th class="num col-v-e-d">D</th>
                <th class="num col-gp-gc">GP</th>
                <th class="num col-gp-gc">GC</th>
                <th class="num">SG</th>
            </tr>
        </thead>
        <tbody>
            {linhas_tabela}
        </tbody>
    </table>'''
else:
    tabela_html = '<div style="padding:2rem; text-align:center; color:#888;">Classificação não disponível.</div>'

if MEU_TIME and MEU_TIME.get("jogadores"):
    jogadores = MEU_TIME["jogadores"]
    nomes_fathur = set()
    if SUGESTAO_FATHUR and SUGESTAO_FATHUR.get("jogadores"):
        nomes_fathur = {j["nome"].lower() for j in SUGESTAO_FATHUR["jogadores"]}

    total = 0
    bonus_capitao = 0
    capitao_nome = ""
    capitao_pts_base = 0
    acertos = 0

    reserva_luxo_nome = SUGESTAO_FATHUR.get("reserva_luxo", "").lower().strip()
    jogadores_titulares = []
    reserva_luxo_jogador = None

    for j in jogadores:
        nome_lower = j.get("nome", "").lower().strip()
        if nome_lower == reserva_luxo_nome:
            reserva_luxo_jogador = j
        else:
            jogadores_titulares.append(j)

    if reserva_luxo_jogador:
        pos_reserva = reserva_luxo_jogador.get("posicao", "").upper()
        pts_reserva = PONTOS_REAIS.get(reserva_luxo_nome, reserva_luxo_jogador.get("pontos", 0) or 0)
        titulares_mesma_pos = [j for j in jogadores_titulares if j.get("posicao", "").upper() == pos_reserva]

        if titulares_mesma_pos:
            pior_titular = min(titulares_mesma_pos, key=lambda x: PONTOS_REAIS.get(x.get("nome", "").lower().strip(), x.get("pontos", 0) or 0))
            pts_pior_titular = PONTOS_REAIS.get(pior_titular.get("nome", "").lower().strip(), pior_titular.get("pontos", 0) or 0)

            if pts_reserva > pts_pior_titular:
                jogadores_titulares.remove(pior_titular)
                jogadores_titulares.append(reserva_luxo_jogador)

    for j in jogadores_titulares:
        nome_original = j.get("nome", "")
        nome_lower = nome_original.lower().strip()
        pts = PONTOS_REAIS.get(nome_lower, j.get("pontos", 0) or 0)

        total += pts
        if j.get("capitao"):
            capitao_nome = nome_original
            capitao_pts_base = pts
            bonus_capitao = pts * 0.5
        if nome_lower in nomes_fathur:
            acertos += 1

    total_com_capitao = total + bonus_capitao
    media = total_com_capitao / len(jogadores_titulares) if jogadores_titulares else 0
    total_meu = len(jogadores_titulares)
    taxa_acerto = (acertos / total_meu * 100) if total_meu > 0 else 0
    
    cards = ""
    for j in jogadores_titulares:
        nome = j.get("nome", "?")
        pts = PONTOS_REAIS.get(nome.lower().strip(), j.get("pontos", 0) or 0)
        classe_neg = "negativo" if pts < 0 else ""
        badge_cap = '<span class="capitao-badge">👑 CAP</span>' if j.get("capitao") else ""
        exibir_pts = pts * 1.5 if j.get("capitao") else pts
        badge_comp = ""
        if SUGESTAO_FATHUR and SUGESTAO_FATHUR.get("jogadores"):
            if nome.lower() in nomes_fathur:
                badge_comp = '<span class="comparador-badge igual">✓ Fathur</span>'
            else:
                badge_comp = '<span class="comparador-badge diferente">⚠ Fathur não</span>'
        cards += f'''<div class="jogador-card">
            <span class="jogador-pos">{j.get("posicao", "?")}</span>
            <span class="jogador-nome">{nome} {badge_cap} {badge_comp}
                <small>{j.get("clube", "")}</small>
            </span>
            <span class="jogador-pts {classe_neg}">{exibir_pts:+.1f}</span>
        </div>'''
        
    stats_html = f'''
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-card-label">Total</div><div class="stat-card-val">{total_com_capitao:.1f}</div><div class="stat-card-sub">com capitão ×1.5</div></div>
        <div class="stat-card"><div class="stat-card-label">Média</div><div class="stat-card-val">{media:.1f}</div><div class="stat-card-sub">por jogador</div></div>
        <div class="stat-card"><div class="stat-card-label">Capitão</div><div class="stat-card-val">{capitao_pts_base * 1.5:.1f}</div><div class="stat-card-sub">{capitao_nome}</div></div>
    </div>
    '''
    if SUGESTAO_FATHUR and total_meu > 0:
        pct_igual = taxa_acerto
        pct_diferente = 100 - taxa_acerto
        barra_html = f'''
        <div class="acerto-wrap">
            <div class="acerto-titulo">⚔️ Acordo com o Fathur FC — {acertos}/{total_meu} jogadores</div>
            <div class="acerto-barra">
                <div class="acerto-barra-igual" style="width:{pct_igual}%">{pct_igual:.0f}%</div>
                <div class="acerto-barra-diferente" style="width:{pct_diferente}%">{pct_diferente:.0f}%</div>
            </div>
            <div class="acerto-legenda">
                <span><i style="background:#16a34a"></i> Igual ao Fathur ({acertos})</span>
                <span><i style="background:#f59e0b"></i> Diferente ({total_meu - acertos})</span>
            </div>
        </div>
        '''
    else:
        barra_html = ""
        
    meu_time_html = f'''
    <div class="meu-time-header">
        <h2>👤 Meu Time</h2>
        <p>Rodada {MEU_TIME.get("rodada", "?")} · {len(jogadores_titulares)} jogadores</p>
    </div>
    {stats_html}
    {barra_html}
    {cards}
    '''
else:
    meu_time_html = '''
    <div class="meu-time-vazio">
        <div class="icone">👤</div>
        <h3>Nenhum time cadastrado</h3>
        <p>Edite o arquivo <code>meu_time.json</code> no repositório.</p>
    </div>
    '''

# Carrega o relatório de análise
analise_html = ""
if os.path.exists('analise_relatorio.html'):
    with open('analise_relatorio.html', 'r', encoding='utf-8') as f:
        analise_html = f.read()

badge = f"🏆 Rodada {RODADA_ATUAL}"
if DATA_RODADA:
    badge += f" • {DATA_RODADA}"

html = html.replace("RODADA_BADGE", badge)
html = html.replace("JOGOS_AQUI", jogos_html)
html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)
html = html.replace("TABELA_AQUI", tabela_html)
html = html.replace("MEU_TIME_AQUI", meu_time_html)
html = html.replace("ANALISE_AQUI", analise_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Site gerado - Rodada {RODADA_ATUAL}")
print(f"Classificação: {len(CLASSIFICACAO)} times")
print(f"Meu Time: {'OK' if MEU_TIME else 'vazio'}")
