import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime
from config import RODADA_ATUAL, DATA_RODADA, JOGOS_RODADA

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
    ("Fortaleza", logo("fortalezaec.net"), "#003366"),
    ("Ceará", logo("cearasc.com"), "#000000"),
    ("Sport", logo("sportrecife.com.br"), "#c8102e"),
    ("Juventude", logo("esporteclubejuventude.com.br"), "#006437"),
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
  .jogos { max-width: 900px; margin: 1.5rem auto 0; padding: 0 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .5rem; }
  .jogo { background: rgba(255,255,255,.15); color: white; padding: .5rem .8rem; border-radius: 8px; font-size: .8rem; text-align: center; }
  .jogo strong { display: block; font-size: .9rem; margin-bottom: .2rem; }
  .busca { max-width: 900px; margin: 1rem auto 2rem; padding: 0 1rem; position: relative; z-index: 10; }
  .busca input { width: 100%; padding: 1rem 1.2rem; font-size: 1rem; border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.1); outline: none; background: white; color: inherit; }
  body.escuro .busca input { background: #1e1e1e; color: #e0e0e0; }
  .busca input:focus { box-shadow: 0 4px 16px rgba(10,92,46,.3); }
  .container { max-width: 900px; margin: 0 auto; padding: 0 1rem 3rem; }
  .time { background: white; border-radius: 12px; margin-bottom: 1rem; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 5px solid #0a5c2e; }
  body.escuro .time { background: #1e1e1e; box-shadow: 0 1px 4px rgba(0,0,0,.3); }
  .time-header { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid #eee; }
  body.escuro .time-header { border-bottom-color: #333; }
  .time-header img { width: 44px; height: 44px; object-fit: contain; }
  .time-header h2 { margin: 0; font-size: 1.15rem; color: #0a5c2e; flex: 1; }
  body.escuro .time-header h2 { color: #4ade80; }
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
  @media (max-width: 600px) {
    header h1 { font-size: 1.3rem; }
    .time-header { flex-wrap: wrap; }
    .time-header h2 { font-size: 1rem; width: 100%; }
    .btn-escalacao { width: 100%; text-align: center; }
    #btn-topo { bottom: 1rem; right: 1rem; }
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

<div class="busca">
  <input type="text" id="campo-busca" placeholder="🔍 Buscar time..." oninput="filtrar()">
</div>

<div class="container">
CONTEUDO_AQUI
</div>

<footer>
  <p>Dados coletados automaticamente do Google News</p>
  <p>Atualização automática 3x ao dia: 8h, 13h, 18h</p>
</footer>

<button id="btn-topo" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

<script>
function filtrar() {
  const termo = document.getElementById('campo-busca').value.toLowerCase();
  document.querySelectorAll('.time').forEach(function(el) {
    const nome = el.getAttribute('data-time').toLowerCase();
    el.classList.toggle('oculto', !nome.includes(termo));
  });
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
        corpo += f'''<div class="time-header">
            <img src="{logo_url}" alt="{nome}" onerror="this.style.display='none'">
            <h2>{nome}</h2>
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
            meta = f'<span>{fonte}</span>'
            if tempo:
                meta += f'<span class="tempo">⏱ {tempo}</span>'
            corpo += f'<div class="noticia"><a href="{link}" target="_blank">{titulo}</a><div class="meta">{meta}</div></div>'
    else:
        corpo += '<div class="vazio">Nenhuma notícia encontrada.</div>'
    corpo += '</div>'

badge = f"🏆 Rodada {RODADA_ATUAL}"
if DATA_RODADA:
    badge += f" • {DATA_RODADA}"

html = html.replace("RODADA_BADGE", badge)
html = html.replace("JOGOS_AQUI", jogos_html)
html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Site gerado - Rodada {RODADA_ATUAL}")
