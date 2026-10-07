import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime
from config import RODADA_ATUAL, DATA_RODADA

conn = sqlite3.connect('dados/escalacoes.db')

TIMES = [
    ("Flamengo", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Flamengo_braz_logo.svg/40px-Flamengo_braz_logo.svg.png", "#c8102e"),
    ("Palmeiras", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/40px-Palmeiras_logo.svg.png", "#006437"),
    ("Corinthians", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Corinthians_simbolo.png/40px-Corinthians_simbolo.png", "#000000"),
    ("São Paulo", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Sao_Paulo_FC_logo.png/40px-Sao_Paulo_FC_logo.png", "#e30613"),
    ("Botafogo", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Botafogo_de_Futebol_e_Regatas_logo.svg/40px-Botafogo_de_Futebol_e_Regatas_logo.svg.png", "#000000"),
    ("Fluminense", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Fluminense_FC_escudo.png/40px-Fluminense_FC_escudo.png", "#7a0d1d"),
    ("Vasco", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Clube_de_Regatas_Vasco_da_Gama_logo.svg/40px-Clube_de_Regatas_Vasco_da_Gama_logo.svg.png", "#000000"),
    ("Grêmio", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Gremio_logo.svg/40px-Gremio_logo.svg.png", "#0d47a1"),
    ("Internacional", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/SC_Internacional_logo.svg/40px-SC_Internacional_logo.svg.png", "#c8102e"),
    ("Cruzeiro", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Cruzeiro_Esporte_Clube_logo.svg/40px-Cruzeiro_Esporte_Clube_logo.svg.png", "#0d47a1"),
    ("Atlético Mineiro", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_Mineiro_logo.svg/40px-Atletico_Mineiro_logo.svg.png", "#000000"),
    ("Bahia", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Esporte_Clube_Bahia_logo.svg/40px-Esporte_Clube_Bahia_logo.svg.png", "#003399"),
    ("Vitória", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Esporte_Clube_Vitoria_logo.svg/40px-Esporte_Clube_Vitoria_logo.svg.png", "#c8102e"),
    ("Fortaleza", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Fortaleza_Esporte_Clube_logo.svg/40px-Fortaleza_Esporte_Clube_logo.svg.png", "#003366"),
    ("Ceará", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Ceara_Sporting_Club_logo.svg/40px-Ceara_Sporting_Club_logo.svg.png", "#000000"),
    ("Sport", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Sport_Club_do_Recife_logo.svg/40px-Sport_Club_do_Recife_logo.svg.png", "#c8102e"),
    ("Juventude", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Esporte_Clube_Juventude_logo.svg/40px-Esporte_Clube_Juventude_logo.svg.png", "#006437"),
    ("Bragantino", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Red_Bull_Bragantino_logo.svg/40px-Red_Bull_Bragantino_logo.svg.png", "#c8102e"),
    ("Mirassol", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Mirassol_Futebol_Clube_logo.svg/40px-Mirassol_Futebol_Clube_logo.svg.png", "#006437"),
    ("Santos", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Santos_Logo.png/40px-Santos_Logo.png", "#000000"),
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
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f0f2f5; color: #1a1a1a; }
  header { background: linear-gradient(135deg, #0a5c2e 0%, #0d7a3f 100%); color: white; padding: 2rem 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
  header h1 { margin: 0; font-size: 1.8rem; }
  .rodada-badge { display: inline-block; background: rgba(255,255,255,.2); color: white; padding: .35rem 1rem; border-radius: 20px; font-size: .85rem; font-weight: 600; margin-top: .75rem; letter-spacing: .5px; }
  header p { margin: .5rem 0 0; opacity: .85; font-size: .9rem; }
  .busca { max-width: 900px; margin: -1.5rem auto 2rem; padding: 0 1rem; position: relative; z-index: 10; }
  .busca input { width: 100%; padding: 1rem 1.2rem; font-size: 1rem; border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.1); outline: none; }
  .busca input:focus { box-shadow: 0 4px 16px rgba(10,92,46,.3); }
  .container { max-width: 900px; margin: 0 auto; padding: 0 1rem 3rem; }
  .time { background: white; border-radius: 12px; margin-bottom: 1rem; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 5px solid #0a5c2e; }
  .time-header { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid #eee; }
  .time-header img { width: 36px; height: 36px; object-fit: contain; }
  .time-header h2 { margin: 0; font-size: 1.15rem; color: #0a5c2e; flex: 1; }
  .btn-escalacao { display: inline-block; background: #0a5c2e; color: white; text-decoration: none; padding: .5rem 1rem; border-radius: 8px; font-size: .85rem; font-weight: 600; transition: all .2s; white-space: nowrap; }
  .btn-escalacao:hover { background: #0d7a3f; transform: translateY(-1px); }
  .noticia { padding: .75rem 1.5rem; border-top: 1px solid #f5f5f5; }
  .noticia:first-of-type { border-top: none; }
  .noticia a { color: #1a4d8f; text-decoration: none; font-weight: 500; font-size: .95rem; }
  .noticia a:hover { text-decoration: underline; }
  .meta { font-size: .75rem; color: #888; margin-top: .25rem; display: flex; gap: 1rem; flex-wrap: wrap; }
  .tempo { color: #0a5c2e; font-weight: 500; }
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
  <h1>⚽ Prováveis Escalações</h1>
  <div class="rodada-badge">RODADA_BADGE</div>
  <p style="margin-top:.75rem;font-size:.8rem;">Atualizado em ATUALIZADO_AQUI</p>
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
    if (nome.includes(termo)) {
      el.classList.remove('oculto');
    } else {
      el.classList.add('oculto');
    }
  });
}

window.addEventListener('scroll', function() {
  const btn = document.getElementById('btn-topo');
  if (window.scrollY > 400) {
    btn.style.display = 'block';
  } else {
    btn.style.display = 'none';
  }
});
</script>
</body>
</html>"""

corpo = ""
for nome, logo, cor in TIMES:
    linhas = conn.execute(
        "SELECT titulo, link, fonte, publicado_em FROM noticias WHERE time=? ORDER BY coletado_em DESC LIMIT 5",
        (nome,)
    ).fetchall()
    
    corpo += f'<div class="time" data-time="{nome}" style="border-left-color:{cor}">'
    
    # Header com logo, nome e botão "Ver escalação"
    if linhas:
        primeiro_link = linhas[0][1]
        corpo += f'''<div class="time-header">
            <img src="{logo}" alt="{nome}" onerror="this.style.display='none'">
            <h2>{nome}</h2>
            <a href="{primeiro_link}" target="_blank" class="btn-escalacao">🟢 Ver escalação</a>
        </div>'''
    else:
        corpo += f'''<div class="time-header">
            <img src="{logo}" alt="{nome}" onerror="this.style.display='none'">
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
html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Site gerado - Rodada {RODADA_ATUAL}")
