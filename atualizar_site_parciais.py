import json
import os
import re

ARQUIVO_PARCIAIS = "parciais.json"
ARQUIVO_MEU_TIME = "meu_time.json"
ARQUIVO_HTML = "index.html"


def _render_jogadores_por_posicao(jogadores):
    if not jogadores:
        return '<div class="parcial-vazio">Sem pontuação</div>'
    por_posicao = {}
    for j in jogadores:
        pos_id = j.get("posicao_id", 0)
        pos_nome = {1: "GOL", 2: "LAT", 3: "ZAG", 4: "MEI", 5: "ATA", 6: "TEC"}.get(pos_id, "OUT")
        por_posicao.setdefault(pos_nome, []).append(j)
    html = ""
    for pos in ["GOL", "LAT", "ZAG", "MEI", "ATA", "TEC"]:
        if pos not in por_posicao:
            continue
        html += f'<div class="parcial-pos-titulo">{pos}</div>'
        for j in por_posicao[pos]:
            scouts = j.get("scout", {}) or {}
            scouts_txt = " ".join(f"{k}({v})" for k, v in scouts.items() if v > 0) if scouts else ""
            html += f'''
            <div class="parcial-jogador">
                <span class="parcial-nome">{j.get("apelido", "?")}</span>
                <span class="parcial-scouts">{scouts_txt}</span>
                <span class="parcial-pts">{j.get("pontuacao", 0):.1f}</span>
            </div>'''
    return html


def gerar_bloco_parciais():
    if not os.path.exists(ARQUIVO_PARCIAIS):
        return '<div class="vazio">Nenhuma parcial disponível.</div>'
    with open(ARQUIVO_PARCIAIS, "r", encoding="utf-8") as f:
        dados = json.load(f)
    atletas = dados.get("atletas", {})
    partidas = dados.get("partidas", [])
    if not atletas:
        return '<div class="vazio">Nenhum atleta pontuou ainda nesta rodada.</div>'
    atletas_por_clube = {}
    for atleta_id, info in atletas.items():
        clube_id = info.get("clube_id")
        if clube_id:
            atletas_por_clube.setdefault(clube_id, []).append(info)
    html_partes = []
    for partida in partidas:
        casa = partida.get("clube_casa", {})
        visitante = partida.get("clube_visitante", {})
        placar_casa = partida.get("placar_oficial_mandante", "?")
        placar_visitante = partida.get("placar_oficial_visitante", "?")
        status = partida.get("partida_status", "")
        if status == "Agendada":
            continue
        casa_id = casa.get("id")
        visitante_id = visitante.get("id")
        sigla_casa = casa.get("abreviacao", "?")
        sigla_visitante = visitante.get("abreviacao", "?")
        jogadores_casa = atletas_por_clube.get(casa_id, [])
        jogadores_visitante = atletas_por_clube.get(visitante_id, [])
        total_casa = sum(j.get("pontuacao", 0) or 0 for j in jogadores_casa)
        total_visitante = sum(j.get("pontuacao", 0) or 0 for j in jogadores_visitante)
        html_partes.append(f'''
        <div class="parcial-jogo">
            <div class="parcial-jogo-header">
                <div class="parcial-placar">
                    <span class="parcial-time-nome">{sigla_casa}</span>
                    <span class="parcial-total">{total_casa:.2f}</span>
                    <span class="parcial-x">x</span>
                    <span class="parcial-total">{total_visitante:.2f}</span>
                    <span class="parcial-time-nome">{sigla_visitante}</span>
                </div>
                <span class="parcial-jogo-status">{status}</span>
            </div>
            <div class="parcial-jogo-corpo">
                <div class="parcial-jogo-lado">{_render_jogadores_por_posicao(jogadores_casa)}</div>
                <div class="parcial-jogo-lado">{_render_jogadores_por_posicao(jogadores_visitante)}</div>
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


def calcular_total_meu_time():
    if not os.path.exists(ARQUIVO_PARCIAIS) or not os.path.exists(ARQUIVO_MEU_TIME):
        print("ERRO: parciais.json ou meu_time.json não encontrados")
        return None
    with open(ARQUIVO_PARCIAIS, "r", encoding="utf-8") as f:
        parciais = json.load(f)
    with open(ARQUIVO_MEU_TIME, "r", encoding="utf-8") as f:
        meu_time = json.load(f)
    atletas_parciais = parciais.get("atletas", {})
    jogadores_meu_time = meu_time.get("jogadores", [])
    print(f"Jogadores no parciais.json: {len(atletas_parciais)}")
    print(f"Jogadores no meu_time.json: {len(jogadores_meu_time)}")
    # Mapeia todos os apelidos do parciais (lower) para pontuação
    mapa_pontos = {}
    for aid, info in atletas_parciais.items():
        apelido = info.get("apelido", "").lower().strip()
        pontos = info.get("pontuacao", 0) or 0
        mapa_pontos[apelido] = pontos
    total = 0
    encontrados = 0
    for j in jogadores_meu_time:
        nome = j.get("nome", "").lower().strip()
        pontos = mapa_pontos.get(nome, 0)
        if nome in mapa_pontos:
            encontrados += 1
            print(f"  ✅ {j.get('nome')}: {pontos} pts")
        else:
            print(f"  ❌ {j.get('nome')}: NÃO encontrado no parciais")
        if j.get("capitao"):
            pontos = pontos * 1.5
        total += pontos
    print(f"Total encontrados: {encontrados}/{len(jogadores_meu_time)}")
    print(f"Total calculado: {total:.1f}")
    return total


def injetar_no_html():
    if not os.path.exists(ARQUIVO_HTML):
        print("AVISO: index.html não encontrado")
        return
    with open(ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    # 1. Injeta as parciais
    bloco = gerar_bloco_parciais()
    if '<!-- PARCIAIS -->' in html:
        html = re.sub(r'<!-- PARCIAIS -->.*?<!-- /PARCIAIS -->', f'<!-- PARCIAIS -->{bloco}<!-- /PARCIAIS -->', html, flags=re.DOTALL)
    else:
        html = html.replace('</footer>', f'{bloco}</footer>')
    # 2. Atualiza o total do Meu Time
    total_ao_vivo = calcular_total_meu_time()
    if total_ao_vivo is not None:
        # Substitui o valor dentro do card de "Total"
        html = re.sub(
            r'(<div class="stat-card-label">Total</div>\s*<div class="stat-card-val">)[^<]*(</div>)',
            rf'\g<1>{total_ao_vivo:.1f}\g<2>',
            html,
            count=1
        )
    with open(ARQUIVO_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("Parciais injetadas e total do Meu Time atualizado")


if __name__ == "__main__":
    injetar_no_html()
