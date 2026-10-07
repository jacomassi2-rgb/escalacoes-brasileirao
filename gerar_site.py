import sqlite3
from datetime import datetime
from config import RODADA_ATUAL, DATA_RODADA

conn = sqlite3.connect('dados/escalacoes.db')

TIMES = [
    ("Flamengo", "https://logo.clearbit.com/flamengo.com.br", "#c8102e"),
    ("Palmeiras", "https://logo.clearbit.com/palmeiras.com.br", "#006437"),
    ("Corinthians", "https://logo.clearbit.com/corinthians.com.br", "#000000"),
    ("São Paulo", "https://logo.clearbit.com/saopaulofc.net", "#e30613"),
    ("Botafogo", "https://logo.clearbit.com/botafogo.com.br", "#000000"),
    ("Fluminense", "https://logo.clearbit.com/fluminense.com.br", "#7a0d1d"),
    ("Vasco", "https://logo.clearbit.com/vasco.com.br", "#000000"),
    ("Grêmio", "https://logo.clearbit.com/gremio.net", "#0d47a1"),
    ("Internacional", "https://logo.clearbit.com/internacional.com.br", "#c8102e"),
    ("Cruzeiro", "https://logo.clearbit.com/cruzeiro.com.br", "#0d47a1"),
    ("Atlético Mineiro", "https://logo.clearbit.com/atletico.com.br", "#000000"),
    ("Bahia", "https://logo.clearbit.com/esporteclubebahia.com.br", "#003399"),
    ("Vitória", "https://logo.clearbit.com/ecvitoria.com.br", "#c8102e"),
    ("Fortaleza", "https://logo.clearbit.com/fortalezaec.net", "#003366"),
    ("Ceará", "https://logo.clearbit.com/cearasc.com", "#000000"),
    ("Sport", "https://logo.clearbit.com/sportrecife.com.br", "#c8102e"),
    ("Juventude", "https://logo.clearbit.com/esporteclubejuventude.com.br", "#006437"),
    ("Bragantino", "https://logo.clearbit.com/redbullbragantino.com.br", "#c8102e"),
    ("Mirassol", "https://logo.clearbit.com/mirassolfc.com.br", "#006437"),
    ("Santos", "https://logo.clearbit.com/santosfc.com.br", "#000000"),
]

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
  .time-header img { width: 40px; height: 40px; object-fit: contain; }
  .time-header h2 { margin: 0; font-size: 1.15rem; color: #0a5c2e; }
  .noticia { padding: .75rem 1.5rem; border-top: 1px solid #f5f5f5; }
  .noticia:first-of-type { border-top: none; }
  .noticia a { color: #1a4d8f; text-decoration: none; font-weight: 500; font-size: .95rem; }
  .noticia a:hover { text-decoration: underline; }
  .meta { font-size: .75rem; color: #888; margin-top: .25rem; }
  .vazio { padding: 1rem 1.5rem; color: #999; font-style: italic; font-size: .9rem; }
  .oculto { display: none !important; }
  footer { text-align: center; padding: 2rem 1rem; color: #888; font-size: .85rem; }
  @media (max-width: 600px) {
    header h1 { font-size: 1.3rem; }
    .time-header h2 { font-size: 1rem; }
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
</script>
</body>
</html>"""

corpo = ""
for nome, logo, cor in TIMES:
    linhas = conn.execute(
        "SELECT titulo, link, fonte FROM noticias WHERE time=? ORDER BY coletado_em DESC LIMIT 5",
        (nome,)
    ).fetchall()
    corpo += f'<div class="time" data-time="{nome}" style="border-left-color:{cor}">'
    corpo += f'<div class="time-header"><img src="{logo}" alt="{nome}" onerror="this.style.display=\'none\'"><h2>{nome}</h2></div>'
    if linhas:
        for titulo, link, fonte in linhas:
            corpo += f'<div class="noticia"><a href="{link}" target="_blank">{titulo}</a><div class="meta">{fonte}</div></div>'
    else:
        corpo += '<div class="vazio">Nenhuma notícia encontrada.</div>'
    corpo += '</div>'

# Monta o badge da rodada
badge = f"🏆 Rodada {RODADA_ATUAL}"
if DATA_RODADA:
    badge += f" • {DATA_RODADA}"

html = html.replace("RODADA_BADGE", badge)
html = html.replace("ATUALIZADO_AQUI", datetime.now().strftime("%d/%m/%Y %H:%M"))
html = html.replace("CONTEUDO_AQUI", corpo)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Site gerado - Rodada {RODADA_ATUAL}")
