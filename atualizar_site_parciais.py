import json
import os
import re

ARQUIVO_PARCIAIS = "parciais.json"
ARQUIVO_HTML = "index.html"


def _render_jogadores(lista):
    """Renderiza lista de jogadores de um clube."""
    if not lista:
        return '<div class="parcial-vazio">Sem pontuação</div>'
    linhas = []
    for a in lista:
        scouts = a.get("scout", {}) or {}
        scouts_txt = " ".join(f"{k}({v})" for k, v in scouts.items() if v > 0) if scouts else ""
        linhas.append(f'''
        <div class="parcial-jogador">
            <span class="parcial-nome">{a.get("apelido", "?")}</span>
            <span class="parcial-scouts">{scouts_txt}</span>
            <span class="parcial-pts">{a.get("pontuacao", 0):.1f}</span>
        </div>''')
    return "".join(linhas)


def gerar_bloco_parciais():
    """Gera o HTML completo da seção de parciais."""
    if not os.path.exists(ARQUIVO_PARCIAIS):
        return '<div class="vazio">Nenhuma parcial disponível.</div>'

    with open(ARQUIVO_PARCIAIS, "r", encoding="utf-8") as f:
        dados = json.load(f)

    atletas = dados.get("atletas", {})
    partidas = dados.get("partidas", [])

    if not atletas:
        return '<div class="vazio">Nenhum atleta pontuou ainda nesta rodada.</div>'

    # Agrupa atletas por clube
    atletas_por_clube = {}
    for atleta_id, info in atletas.items():
        clube_id = info.get("clube_id")
        if clube_id:
            atletas_por_clube.setdefault(clube_id, []).append(info)

    # Ordena cada clube por pontos
    for clube_id in atletas_por_clube:
        atletas_por_clube[clube_id].sort(
            key=lambda a: a.get("pontuacao", 0) or 0, reverse=True
        )

    # Gera HTML por jogo
    html_partes = []
    for partida in partidas:
        casa = partida.get("clube_casa", {})
        visitante = partida.get("clube_visitante", {})
        placar_casa = partida.get("placar_oficial_mandante", "?")
        placar_visitante = partida.get("placar_oficial_visitante", "?")
        status = partida.get("partida_status", "")

        # Só mostra jogos que já começaram
        if status == "Agendada":
            continue

        casa_id = casa.get("id")
        visitante_id = visitante.get("id")
        sigla_casa = casa.get("abreviacao", "?")
        sigla_visitante = visitante.get("abreviacao", "?")

        jogadores_casa = atletas_por_clube.get(casa_id, [])
        jogadores_visitante = atletas_por_clube.get(visitante_id, [])

        if not jogadores_casa and not jogadores_visitante:
            continue

        html_partes.append(f'''
        <div class="parcial-jogo">
            <div class="parcial-jogo-header">
                <span class="parcial-jogo-time">{sigla_casa} {placar_casa} x {placar_visitante} {sigla_visitante}</span>
                <span class="parcial-jogo-status">{status}</span>
            </div>
            <div class="parcial-jogo-corpo">
                <div class="parcial-jogo-lado">{_render_jogadores(jogadores_casa)}</div>
                <div class="parcial-jogo-lado">{_render_jogadores(jogadores_visitante)}</div>
            </div>
        </div>
        ''')

    ts = dados.get("ts", "")
    conteudo = "".join(html_partes) if html_partes else '<div class="vazio">Nenhum jogo em andamento.</div>'

    return f'''
    <div class="parciais-container">
        <div class="parciais-header">
            <span>🔴 Parciais ao vivo</span>
            <span class="parciais-ts">{ts}</span>
        </div>
        {conteudo}
    </div>
    '''


def injetar_no_html():
    """Substitui o bloco <!-- PARCIAIS --> no index.html."""
    if not os.path.exists(ARQUIVO_HTML):
        print("AVISO: index.html não encontrado")
        return

    with open(ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    bloco = gerar_bloco_parciais()

    if '<!-- PARCIAIS -->' in html:
        html = re.sub(
            r'<!-- PARCIAIS -->.*?<!-- /PARCIAIS -->',
            f'<!-- PARCIAIS -->{bloco}<!-- /PARCIAIS -->',
            html,
            flags=re.DOTALL,
        )
    else:
        print("AVISO: placeholder <!-- PARCIAIS --> não encontrado")
        html = html.replace('</footer>', f'{bloco}</footer>')

    with open(ARQUIVO_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("Parciais injetadas no HTML")


if __name__ == "__main__":
    injetar_no_html()
