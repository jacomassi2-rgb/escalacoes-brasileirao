import sqlite3
import json
import os
import re
import unicodedata
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
        if segundos < 60:
            return "agora mesmo"
        elif segundos < 3600:
            return f"há {segundos // 60} min"
        elif segundos < 86400:
            return f"há {segundos // 3600} h"
        else:
            return f"há {segundos // 86400} dias"
    except:
        return ""

def tempo_em_horas(data_str):
    try:
        dt = parsedate_to_datetime(data_str)
        agora = datetime.now(dt.tzinfo)
        return (agora - dt).total_seconds() / 3600
    except:
        return 9999

def normalizar_nome(s):
    """Remove acentos e deixa minúsculo pra busca."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

# ============================================
# CARREGA MEU TIME
# ============================================
MEU_TIME = {}
if os.path.exists('meu_time.json'):
    with open('meu_time.json', 'r', encoding='utf-8') as f:
        MEU_TIME = json.load(f)

# ============================================
# CARREGA SUGESTÃO FATHUR
# ============================================
SUGESTAO_FATHUR = {}
if os.path.exists('sugestao_fathur.json'):
    with open('sugestao_fathur.json', 'r', encoding='utf-8') as f:
        SUGESTAO_FATHUR = json.load(f)

# ============================================
# 🔔 BUSCA ALERTAS NAS NOTÍCIAS
# ============================================
def buscar_alertas_jogador(nome_jogador):
    """Busca notícias que mencionam o jogador + palavras-chave."""
    if not nome_jogador:
        return []
    
    nome_norm = normalizar_nome(nome_jogador)
    if len(nome_norm) < 3:
        return []
    
    # Palavras que indicam problema (🔴)
    negativas = ["lesão", "lesao", "lesionado", "dúvida", "duvida", 
                 "suspenso", "suspensao", "suspensão", "cortado", "fora",
                 "poupado", "poupanca", "poupança", "não joga", "nao joga",
                 "desfalque", "contundido", "machucado", "departamento médico"]
    
    # Palavras que indicam OK (🟢)
    positivas = ["confirmado", "titular", "retorna", "volta", "escalado",
                 "à disposição", "a disposicao", "disponível", "disponivel",
                 "recuperado", "pronto", "joga"]
    
    try:
        linhas = conn.execute(
            "SELECT titulo, link, fonte, publicado_em FROM noticias WHERE lower(titulo) LIKE ? ORDER BY coletado_em DESC LIMIT 10",
            (f"%{nome_norm}%",)
        ).fetchall()
    except:
        return []
    
    alertas = []
    for titulo, link, fonte, publicado_em in linhas:
        titulo_norm = normalizar_nome(titulo)
        
        # Checa se o nome está realmente no título (evita falsos positivos)
        if nome_norm not in titulo_norm:
            continue
        
        # Verifica palavras-chave
        tem_negativa = any(p in titulo_norm for p in negativas)
        tem_positiva = any(p in titulo_norm for p in positivas)
        
        if tem_negativa:
            alertas.append({
                "tipo": "negativo",
                "titulo": titulo,
                "link": link,
                "fonte": fonte,
                "tempo": tempo_relativo(publicado_em)
            })
        elif tem_positiva:
            alertas.append({
                "tipo": "positivo",
                "titulo": titulo,
                "link": link,
                "fonte": fonte,
                "tempo": tempo_relativo(publicado_em)
            })
    
    # Retorna o alerta mais recente de cada tipo
    return alertas[:2]


# ============================================
# HTML
# ============================================
html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prováveis Escalações - Brasileirão</title>
<style>
  * { box-sizing: border-box; transition: background .3s, color .3s; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f0f2f5; color: #1a1a1a; }
  body.escuro { background: #121212; color: #e0e0e0; }
  header { background: linear-gradient(135deg, #0a5c2e 0%, #0d7a3f 100%); color: white; padding: 2rem 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.1); position: relative; }
  header h1 { margin: 0; font-size: 1.8rem; }
  .btn-tema { position: absolute; top: 1rem; right: 1rem; background: rgba(255,255,255,.2); border: none; color: white; padding: .5rem .9rem; border-radius: 20px; cursor: pointer; font-size: .9rem; }
  .btn-tema:hover { background: rgba(255,255,255,.3); }
  .rodada-badge { display: inline-block; background: rgba(255,255,255,.2); color: white; padding: .35rem 1rem; border-radius: 20px; font-size: .85rem; font-weight: 600; margin-top: .75rem; letter-spacing: .5px; }
  header p { margin: .5rem 0 0; opacity: .85; font-size: .9rem; }
  .jogos { max-width: 900px; margin: 1.5rem auto 0; padding: 0 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: .5rem; }
  .jogo { background: rgba(255,255,255,.15); color: white; padding: .5rem .8rem; border-radius: 8px; font-size: .8rem; text-align: center; }
  .jogo strong { display: block; font-size: .9rem; margin-bottom: .2rem; }
  .abas { max-width: 900px; margin: 1rem auto 0; padding: 0 1rem; display: flex; gap: .5rem; flex-wrap: wrap; }
  .aba-btn { flex: 1; min-width: 140px; padding: .8rem 1rem; background: white; border: 2px solid transparent; border-radius: 12px; font-size: .9rem; font-weight: 700; cursor: pointer; color: #0a5c2e; box-shadow: 0 2px 6px rgba(0,0,0,.05); transition: all .2s; }
  body.escuro .aba-btn { background: #1e1e1e; color: #4ade80; }
  .aba-btn.ativo { background: #0a5c2e; color: white; border-color: #0a5c2e; }
  body.escuro .aba-btn.ativo { background: #0d7a3f; color: white; }
  .aba-conteudo { display: none; }
  .aba-conteudo.ativo { display: block; }
  .controles { max-width: 900px; margin: 1rem auto 2rem; padding: 0 1rem; display: flex; gap: .5rem; flex-wrap: wrap; }
  .controles input { flex: 1; min-width: 200px; padding: 1rem 1.2rem; font-size: 1rem; border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.1); outline: none; background: white; color: inherit; }
  body.escuro .controles input { background: #1e1e1e; color: #e0e0e0; }
  .btn-filtro { background: white; border: none; padding: .8rem 1.2rem; border-radius: 12px; font-size: .85rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,.1); color: #0a5c2e; white-space: nowrap; }
  body.escuro .btn-filtro { background: #1e1e1e; color: #4ade80; }
  .btn-filtro.ativo { background: #0a5c2e; color: white; }
  .container { max-width: 900px; margin: 0 auto; padding: 0 1rem 3rem; }
  .time { background: white; border-radius: 12px; margin-bottom: 1rem; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 5px solid #0a5c2e; }
  body.escuro .time { background: #1e1e1e; box-shadow: 0 1px 4px rgba(0,0,0,.3); }
  .time-header { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid #eee; }
  body.escuro .time-header { border-bottom-color: #333; }
  .time-header img { width: 44px; height: 44px; object-fit: contain; }
  .time-header h2 { margin: 0; font-size: 1.15rem; color: #0a5c2e; flex: 1; }
  body.escuro .time-header h2 { color: #4ade80; }
  .contador { background: #f0f2f5; color: #666; padding: .2rem .6rem; border-radius: 20px; font-size: .75rem; font-weight: 600; }
  body.escuro .contador { background: #2a2a2a; color: #aaa; }
  .btn-escalacao { display: inline-block; background: #0a5c2e; color: white; text-decoration: none; padding: .5rem 1rem; border-radius: 8px; font-size: .85rem; font-weight: 600; white-space: nowrap; }
  .btn-escalacao:hover { background: #0d7a3f; }
  .noticia { padding: .75rem 1.5rem; border-top: 1px solid #f5f5f5; }
  body.escuro .noticia { border-top-color: #2a2a2a; }
  .noticia a { color: #1a4d8f; text-decoration: none; font-weight: 500; font-size: .95rem; }
  body.escuro .noticia a { color: #60a5fa; }
  .noticia a:hover { text-decoration: underline; }
  .meta { font-size: .75rem; color: #888; margin-top: .25rem; display: flex; gap: 1rem; flex-wrap: wrap; }
  .tempo { color: #0a5c2e; font-weight: 500; }
  body.escuro .tempo { color: #4ade80; }
  .vazio { padding: 1rem 1.5rem; color: #999; font-style: italic; font-size: .9rem; }
  .oculto { display: none !important; }
  footer { text-align: center; padding: 2rem 1rem; color: #888; font-size: .85rem; }
  #btn-topo { position: fixed; bottom: 2rem; right: 2rem; background: #0a5c2e; color: white; border: none; width: 48px; height: 48px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,.2); display: none; z-index: 100; }
  #btn-topo:hover { background: #0d7a3f; }
  .info-filtro { max-width: 900px; margin: -.5rem auto 1rem; padding: 0 1rem; font-size: .85rem; color: #666; }
  body.escuro .info-filtro { color: #aaa; }
  .tabela-wrap { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  body.escuro .tabela-wrap { background: #1e1e1e; }
  table.classificacao { width: 100%; border-collapse: collapse; font-size: .9rem; }
  table.classificacao thead { background: #0a5c2e; color: white; }
  table.classificacao th { padding: .75rem .5rem; text-align: left; font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; }
  table.classificacao th.num { text-align: center; }
  table.classificacao td { padding: .65rem .5rem; border-bottom: 1px solid #f0f0f0; }
  body.escuro table.classificacao td { border-bottom-color: #2a2a2a; }
  table.classificacao tr:last-child td { border-bottom: none; }
  table.classificacao td.num { text-align: center; font-variant-numeric: tabular-nums; }
  table.classificacao .pos { font-weight: 700; width: 40px; text-align: center; border-radius: 6px; padding: .35rem 0; display: inline-block; min-width: 32px; }
  table.classificacao .time-nome { font-weight: 600; }
  table.classificacao tr.g4 .pos { background: #0a5c2e; color: white; }
  table.classificacao tr.g5-g8 .pos { background: #3b82f6; color: white; }
  table.classificacao tr.g9-g16 .pos { background: #e5e7eb; color: #333; }
  table.classificacao tr.z4 .pos { background: #dc2626; color: white; }
  table.classificacao tr.libertadores { background: rgba(10, 92, 46, .04); }
  table.classificacao tr.pre-libertadores { background: rgba(59, 130, 246, .04); }
  table.classificacao tr.rebaixamento { background: rgba(220, 38, 38, .04); }
  .legenda { max-width: 900px; margin: 1rem auto; padding: 0 1rem; display: flex; gap: 1rem; flex-wrap: wrap; font-size: .8rem; color: #666; }
  body.escuro .legenda { color: #aaa; }
  .legenda span { display: inline-flex; align-items: center; gap: .4rem; }
  .legenda i { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  .meu-time-header { background: linear-gradient(135deg, #0a5c2e, #0d7a3f); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; }
  .meu-time-header h2 { margin: 0 0 .5rem 0; font-size: 1.2rem; }
  .meu-time-header p { margin: 0; opacity: .9; font-size: .9rem; }
  .meu-time-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem; }
  .meu-time-stat { text-align: center; }
  .meu-time-stat-label { font-size: .75rem; opacity: .85; text-transform: uppercase; letter-spacing: .5px; }
  .meu-time-stat-val { font-size: 1.6rem; font-weight: 800; margin-top: .25rem; }
  .jogador-card { background: white; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: .75rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 4px solid #0a5c2e; }
  body.escuro .jogador-card { background: #1e1e1e; }
  .jogador-pos { background: #f0f2f5; color: #666; padding: .3rem .6rem; border-radius: 6px; font-size: .7rem; font-weight: 800; text-transform: uppercase; }
  body.escuro .jogador-pos { background: #2a2a2a; color: #aaa; }
  .jogador-nome { flex: 1; font-weight: 700; font-size: 1rem; }
  .jogador-nome small { display: block; font-weight: 400; color: #888; font-size: .75rem; margin-top: .15rem; }
  .jogador-pts { font-size: 1.3rem; font-weight: 800; color: #0a5c2e; min-width: 60px; text-align: right; }
  body.escuro .jogador-pts { color: #4ade80; }
  .jogador-pts.negativo { color: #dc2626; }
  .capitao-badge { background: #f59e0b; color: white; padding: .2rem .5rem; border-radius: 6px; font-size: .65rem; font-weight: 800; }
  .meu-time-vazio { text-align: center; padding: 3rem 1rem; color: #888; }
  .meu-time-vazio .icone { font-size: 3rem; margin-bottom: 1rem; }
  .aviso-api { background: #fef3c7; border-left: 4px solid #f59e0b; padding: .75rem 1rem; border-radius: 8px; margin-bottom: 1rem; font-size: .85rem; color: #78350f; }
  body.escuro .aviso-api { background: #422006; color: #fbbf24; }
  
  /* ===== ALERTAS ===== */
  .alerta-card { display: flex; align-items: flex-start; gap: .75rem; padding: .9rem 1.1rem; border-radius: 10px; margin-bottom: .6rem; text-decoration: none; transition: transform .15s; }
  .alerta-card:hover { transform: translateY(-1px); }
  .alerta-card.negativo { background: #fef2f2; border-left: 4px solid #dc2626; color: #7f1d1d; }
  .alerta-card.positivo { background: #f0fdf4; border-left: 4px solid #16a34a; color: #14532d; }
  body.escuro .alerta-card.negativo { background: #3f1010; color: #fca5a5; }
  body.escuro .alerta-card.positivo { background: #0d2a17; color: #86efac; }
  .alerta-icon { font-size: 1.2rem; flex-shrink: 0; }
  .alerta-info { flex: 1; min-width: 0; }
  .alerta-titulo { font-weight: 600; font-size: .9rem; line-height: 1.3; }
  .alerta-meta { font-size: .75rem; opacity: .8; margin-top: .25rem; }
  
  /* ===== COMPARADOR ===== */
  .comparador-badge { display: inline-flex; align-items: center; gap: .3rem; padding: .15rem .5rem; border-radius: 6px; font-size: .7rem; font-weight: 700; margin-left: .5rem; }
  .comparador-badge.igual { background: #d1fae5; color: #065f46; }
  .comparador-badge.diferente { background: #fef3c7; color: #92400e; }
  .comparador-badge.faltando { background: #fee2e2; color: #991b1b; }
  body.escuro .comparador-badge.igual { background: #064e3b; color: #6ee7b7; }
  body.escuro .comparador-badge.diferente { background: #451a03; color: #fcd34d; }
  body.escuro .comparador-badge.faltando { background: #450a0a; color: #fca5a5; }
  
  /* ===== ESTATÍSTICAS ===== */
  .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
  .stat-card { background: white; border-radius: 12px; padding: 1.25rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  body.escuro .stat-card { background: #1e1e1e; }
  .stat-card-label { font-size: .75rem; color: #666; text-transform: uppercase; letter-spacing: .5px; font-weight: 600; }
  body.escuro .stat-card-label { color: #aaa; }
  .stat-card-val { font-size: 1.8rem; font-weight: 800; color: #0a5c2e; margin-top: .35rem; }
  body.escuro .stat-card-val { color: #4ade80; }
  .stat-card-sub { font-size: .75rem; color: #888; margin-top: .25rem; }
  .acerto-wrap { background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  body.escuro .acerto-wrap { background: #1e1e1e; }
  .acerto-titulo { font-size: .8rem; font-weight: 700; color: #666; text-transform: uppercase; letter-spacing: .5px; margin-bottom: .75rem; }
  body.escuro .acerto-titulo { color: #aaa; }
  .acerto-barra { height: 24px; background: #f0f2f5; border-radius: 12px; overflow: hidden; display: flex; }
  body.escuro .acerto-barra { background: #2a2a2a; }
  .acerto-barra-igual { background: linear-gradient(90deg, #16a34a, #22c55e); display: flex; align-items: center; justify-content: center; color: white; font-size: .8rem; font-weight: 700; transition: width .4s; }
  .acerto-barra-diferente { background: linear-gradient(90deg, #f59e0b, #fbbf24); display: flex; align-items: center; justify-content: center; color: white; font-size: .8rem; font-weight: 700; transition: width .4s; }
  .acerto-legenda { display: flex; gap: 1rem; margin-top: .75rem; font-size: .8rem; }
  .acerto-legenda span { display: inline-flex; align-items: center; gap: .4rem; }
  .acerto-legenda i { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  
  @media (max-width: 600px) {
    header h1 { font-size: 1.3rem; }
    .time-header { flex-wrap: wrap; }
    .time-header h2 { font-size: 1rem; }
    .btn-escalacao { width: 100%; text-align: center; margin-top: .5rem; }
    #btn-topo { bottom: 1rem; right: 1rem; }
    .controles { flex-direction: column; }
    table.classificacao { font-size: .8rem; }
    table.classificacao th, table.classificacao td { padding: .5rem .3rem; }
    table.classificacao .col-v-e-d, table.classificacao .col-gp-gc { display: none; }
    .meu-time-stats { grid-template-columns: 1fr; }
    .stats-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<header>
  <button class="btn-tema" onclick="alternarTema()">🌙 Tema</button>
  <h1>⚽ Prováveis Escalações</h1>
  <div class="rodada-badge">RODADA_BADGE</div>
  <p style="margin-top:.75rem;font-size:.8rem;">Atualizado em ATUALIZADO_AQUI</p>
  <div class="jogos">JOGOS_AQUI</div>
</header>

<div class="abas">
  <button class="aba-btn ativo" data-aba="noticias" onclick="mudarAba('noticias')">📰 Notícias</button>
  <button class="aba-btn" data-aba="classificacao" onclick="mudarAba('classificacao')">🏆 Classificação</button>
  <button class="aba-btn" data-aba="meu-time" onclick="mudarAba('meu-time')">👤 Meu Time</button>
</div>

<div class="aba-conteudo ativo" id="aba-noticias">
  <div class="controles">
    <input type="text" id="campo-busca" placeholder="🔍 Buscar time..." oninput="filtrar()">
    <button class="btn-filtro" id="btn-24h" onclick="toggle24h()">🕐 Últimas 24h</button>
  </div>
  <div class="info-filtro" id="info-filtro"></div>
  <div class="container">
    CONTEUDO_AQUI
  </div>
</div>

<div class="aba-conteudo" id="aba-classificacao">
  <div class="container">
    <div class="tabela-wrap">TABELA_AQUI</div>
    <div class="legenda">
      <span><i style="background:#0a5c2e"></i> G4 (Libertadores)</span>
      <span><i style="background:#3b82f6"></i> G5-G8 (Pré-Libertadores)</span>
      <span><i style="background:#e5e7eb"></i> Meio da tabela</span>
      <span><i style="background:#dc2626"></i> Z4 (Rebaixamento)</span>
    </div>
  </div>
</div>

<div class="aba-conteudo" id="aba-meu-time">
  <div class="container">
    <div class="aviso-api">
      ⚠️ <b>Modo manual:</b> Edite o arquivo <code>meu_time.json</code> no GitHub para cadastrar seu time e a pontuação de cada jogador.
      👑 O capitão tem pontuação <b>×1.5</b>.
    </div>
    <div id="meu-time-conteudo">
      MEU_TIME_AQUI
    </div>
  </div>
</div>

<footer>
  <p>Dados coletados automaticamente do Google News</p>
  <p>Atualização automática 3x ao dia: 8h, 13h, 18h</p>
</footer>

<button id="btn-topo" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

<script>
let filtro24h = false;

function mudarAba(nome) {
  document.querySelectorAll('.aba-btn').forEach(b => b.classList.toggle('ativo', b.dataset.aba === nome));
  document.querySelectorAll('.aba-conteudo').forEach(c => c.classList.toggle('ativo', c.id === 'aba-' + nome));
}

function filtrar() {
  const termo = document.getElementById('campo-busca').value.toLowerCase();
  document.querySelectorAll('#aba-noticias .time').forEach(function(el) {
    const nome = el.getAttribute('data-time').toLowerCase();
    el.classList.toggle('oculto', !nome.includes(termo));
  });
}

function toggle24h() {
  filtro24h = !filtro24h;
  document.getElementById('btn-24h').classList.toggle('ativo', filtro24h);
  document.querySelectorAll('#aba-noticias .time').forEach(function(el) {
    el.querySelectorAll('.noticia').forEach(function(n) {
      const horas = parseFloat(n.getAttribute('data-horas') || 9999);
      n.classList.toggle('oculto', filtro24h && horas > 24);
    });
    const visiveis = el.querySelectorAll('.noticia:not(.oculto)').length;
    const vazio = el.querySelector('.vazio-24h');
    if (vazio) vazio.classList.toggle('oculto', !filtro24h || visiveis > 0);
    const temAlguma = visiveis > 0 || (!filtro24h && el.querySelectorAll('.noticia').length > 0);
    el.classList.toggle('oculto', filtro24h && !temAlguma);
  });
  document.getElementById('info-filtro').textContent = filtro24h ? '🕐 Mostrando apenas notícias das últimas 24 horas' : '';
}

window.addEventListener('scroll', function() {
  document.getElementById('btn-topo').style.display = window.scrollY > 400 ? 'block' : 'none';
});

function alternarTema() {
  document.body.classList.toggle('escuro');
  localStorage.setItem('tema', document.body.classList.contains('escuro') ? 'escuro' : 'claro');
}
if (localStorage.getItem('tema') === 'escuro') document.body.classList.add('escuro');
</script>
</body>
</html>"""


# ============================================
# MONTA JOGOS
# ============================================
if JOGOS_RODADA:
    jogos_html = "".join(
        f'<div class="jogo"><strong>{casa} x {vis}</strong>{dia}</div>'
        for casa, vis, dia in JOGOS_RODADA
    )
else:
    jogos_html = ""


# ============================================
# MONTA NOTÍCIAS
# ============================================
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


# ============================================
# MONTA TABELA
# ============================================
if CLASSIFICACAO:
    linhas_tabela = ""
    for t in CLASSIFICACAO:
        pos = t["posicao"]
        if pos <= 4:
            classe = "g4 libertadores"
        elif pos <= 8:
            classe = "g5-g8 pre-libertadores"
        elif pos <= 16:
            classe = "g9-g16"
        else:
            classe = "z4 rebaixamento"
        
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


# ============================================
# MONTA MEU TIME (com alertas + comparador + estatísticas)
# ============================================
if MEU_TIME and MEU_TIME.get("jogadores"):
    jogadores = MEU_TIME["jogadores"]
    
    # Lista de nomes do Fathur pra comparação
    nomes_fathur = set()
    if SUGESTAO_FATHUR and SUGESTAO_FATHUR.get("jogadores"):
        nomes_fathur = {j["nome"].lower() for j in SUGESTAO_FATHUR["jogadores"]}
    
    # Cálculos
    total = 0
    bonus_capitao = 0
    capitao_nome = ""
    capitao_pts_base = 0
    acertos = 0
    for j in jogadores:
        pts = j.get("pontos", 0) or 0
        total += pts
        if j.get("capitao"):
            capitao_nome = j.get("nome", "")
            capitao_pts_base = pts
            bonus_capitao = pts * 0.5
        # Conta acertos vs Fathur
        if j.get("nome", "").lower() in nomes_fathur:
            acertos += 1
    total_com_capitao = total + bonus_capitao
    media = total_com_capitao / len(jogadores) if jogadores else 0
    
    # Comparador geral
    total_fathur = len(nomes_fathur)
    total_meu = len(jogadores)
    taxa_acerto = (acertos / total_meu * 100) if total_meu > 0 else 0
    
    # ===== ALERTAS =====
    alertas_html = ""
    total_alertas = 0
    for j in jogadores:
        nome = j.get("nome", "")
        if not nome:
            continue
        alertas = buscar_alertas_jogador(nome)
        for a in alertas:
            total_alertas += 1
            icone = "🔴" if a["tipo"] == "negativo" else "🟢"
            alertas_html += f'''<a href="{a["link"]}" target="_blank" class="alerta-card {a["tipo"]}">
                <span class="alerta-icon">{icone}</span>
                <div class="alerta-info">
                    <div class="alerta-titulo"><b>{nome}</b> — {a["titulo"]}</div>
                    <div class="alerta-meta">{a["fonte"]} · {a["tempo"]}</div>
                </div>
            </a>'''
    
    if total_alertas > 0:
        alertas_wrap = f'''
        <div class="acerto-wrap">
            <div class="acerto-titulo">🔔 Alertas nas notícias ({total_alertas})</div>
            {alertas_html}
        </div>
        '''
    else:
        alertas_wrap = '''<div class="acerto-wrap"><div class="acerto-titulo">🔔 Alertas nas notícias</div><div style="color:#888; font-size:.9rem;">Nenhum alerta nas últimas notícias.</div></div>'''
    
    # ===== CARDS DOS JOGADORES (com comparador) =====
    cards = ""
    for j in jogadores:
        nome = j.get("nome", "?")
        pts = j.get("pontos", 0) or 0
        classe_neg = "negativo" if pts < 0 else ""
        badge_cap = '<span class="capitao-badge">👑 CAP</span>' if j.get("capitao") else ""
        exibir_pts = pts * 1.5 if j.get("capitao") else pts
        
        # Comparador
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
    
    # ===== ESTATÍSTICAS =====
    stats_html = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-card-label">Total</div>
            <div class="stat-card-val">{total_com_capitao:.1f}</div>
            <div class="stat-card-sub">com capitão ×1.5</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Média</div>
            <div class="stat-card-val">{media:.1f}</div>
            <div class="stat-card-sub">por jogador</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Capitão</div>
            <div class="stat-card-val">{capitao_pts_base * 1.5:.1f}</div>
            <div class="stat-card-sub">{capitao_nome}</div>
        </div>
    </div>
    '''
    
    # ===== BARRA DE ACERTO =====
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
        <p>Rodada {MEU_TIME.get("rodada", "?")} · {len(jogadores)} jogadores</p>
    </div>
    {stats_html}
    {barra_html}
    {alertas_wrap}
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


# ============================================
# MONTA HTML FINAL
# ============================================
badge = f"🏆 Rodada {RODADA_ATUAL}"
if DATA_RODADA:
    badge += f" • {DATA_RODADA}"

html = html.replace("RODADA_BADGE", badge)
html = html.replace("JOGOS_AQUI", jogos_html)
html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)
html = html.replace("TABELA_AQUI", tabela_html)
html = html.replace("MEU_TIME_AQUI", meu_time_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Site gerado - Rodada {RODADA_ATUAL}")
print(f"Classificação: {len(CLASSIFICACAO)} times")
print(f"Meu Time: {'OK' if MEU_TIME else 'vazio'}")
print(f"Alertas gerados: {sum(1 for j in MEU_TIME.get('jogadores', []) if buscar_alertas_jogador(j.get('nome', '')))} jogadores com alerta")
