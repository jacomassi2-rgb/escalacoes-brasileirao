# ============================================================
# SCRIPT COMPLETO DEFINITIVO: gerar_site.py (VERSÃO VISUAL)
# ============================================================
import os
import json
import subprocess

if os.path.exists("/content/drive/MyDrive/fathur_fc"):
    BASE_DIR = "/content/drive/MyDrive/fathur_fc"
else:
    BASE_DIR = os.getcwd()

def carregar_json(nome_arquivo):
    caminho = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def gerar_html():
    analise_scouts = carregar_json("analise_scouts.json")
    top5_posicoes = carregar_json("top5_posicoes.json")

    js_analise = json.dumps(analise_scouts, ensure_ascii=False) if analise_scouts else "{}"
    js_top5 = json.dumps(top5_posicoes, ensure_ascii=False) if top5_posicoes else "{}"

    html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fathur FC — Análise Cartola</title>
    <style>
        :root { --bg-color: #121212; --card-bg: #1e1e1e; --text-color: #e0e0e0; --accent: #00b894; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 0; }
        header { background-color: #000; padding: 15px 20px; text-align: center; border-bottom: 2px solid var(--accent); }
        header h1 { margin: 0; font-size: 1.5rem; }
        .tabs { display: flex; background-color: #000; justify-content: center; gap: 10px; padding: 10px; }
        .tab-btn { background: none; border: none; color: #888; padding: 10px 20px; font-size: 1rem; cursor: pointer; border-bottom: 2px solid transparent; transition: 0.3s; }
        .tab-btn.active { color: var(--accent); border-bottom: 2px solid var(--accent); font-weight: bold; }
        .container { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Estilos Filtros */
        .filters { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; background-color: var(--card-bg); padding: 15px; border-radius: 8px; }
        .filter-group { display: flex; flex-direction: column; }
        .filter-group label { font-size: 0.8rem; color: #888; margin-bottom: 5px; }
        .filter-group select { background-color: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 4px; }
        
        /* Estilos para os Cards de Scouts (Barras) */
        .scout-card { background-color: var(--card-bg); margin-bottom: 15px; padding: 15px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; }
        .scout-info { flex: 1; }
        .scout-name { font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
        .scout-club { font-size: 0.9rem; color: #888; }
        
        .scout-bars { flex: 2; display: flex; flex-direction: column; gap: 5px; padding: 0 20px; }
        .bar-row { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; }
        .bar-label { width: 100px; text-align: right; color: #ccc; }
        .bar-container { flex: 1; background-color: #333; height: 20px; border-radius: 10px; overflow: hidden; display: flex; }
        .bar-fill { height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px; font-size: 0.75rem; font-weight: bold; color: #fff; }
        .bar-green { background-color: #00b894; } /* Representa o "Feito" */
        .bar-red { background-color: #d63031; } /* Representa o "Cedido" ou outro scout */
        
        /* Estilos Top 5 */
        .top5-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
        .top5-card { background-color: var(--card-bg); padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent); }
        .top5-card h3 { margin: 0 0 10px 0; font-size: 1.1rem; color: var(--accent); border-bottom: 1px solid #333; padding-bottom: 5px; }
        .top5-card p { margin: 5px 0; font-size: 0.9rem; display: flex; justify-content: space-between; }
        
        /* Classificação */
        #classificacao-container { background-color: var(--card-bg); padding: 20px; border-radius: 8px; text-align: center; }
        .live-badge { background-color: red; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; animation: blink 1s infinite; margin-left: 10px; vertical-align: middle; }
        @keyframes blink { 50% { opacity: 0; } }
        .erro-msg { color: #d63031; text-align: center; padding: 20px; }
    </style>
</head>
<body>
<header>
    <h1>⚽ Fathur FC — Análise e Estratégia</h1>
</header>
<div class="tabs">
    <button class="tab-btn active" onclick="openTab('classificacao', event)">🏆 Classificação</button>
    <button class="tab-btn" onclick="openTab('top5', event)">⭐ Top 5 Posições</button>
    <button class="tab-btn" onclick="openTab('scouts', event)">📊 Cruzamento de Scouts</button>
</div>
<div class="container">
    <div id="classificacao" class="tab-content active">
        <div id="classificacao-container">
            <h2>Campeonato Brasileiro Série A <span class="live-badge">AO VIVO</span></h2>
            <iframe src="https://ge.globo.com/futebol/brasileirao-serie-a/tabela/" width="100%" height="600" frameborder="0" style="border-radius: 8px; margin-top: 15px;"></iframe>
        </div>
    </div>
    
    <div id="top5" class="tab-content">
        <h2>Top 5 Melhores Opções (Média Últimos 5 jogos)</h2>
        <div id="top5-container" class="top5-container"></div>
    </div>
    
    <div id="scouts" class="tab-content">
        <h2>Cruzamento de Scouts por Posição</h2>
        <div class="filters">
            <div class="filter-group">
                <label>Posição</label>
                <select id="filtro-posicao" onchange="renderScouts()">
                    <option value="GOL">Goleiros</option><option value="LAT">Laterais</option>
                    <option value="ZAG">Zagueiros</option><option value="MEI">Meias</option>
                    <option value="ATA">Atacantes</option><option value="TEC">Técnicos</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Período</label>
                <select id="filtro-periodo" onchange="renderScouts()">
                    <option value="ultimos_5">Últimos 5 jogos</option>
                    <option value="ultimos_3">Últimos 3 jogos</option>
                    <option value="total">Total (Histórico)</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Mando de Campo</label>
                <select id="filtro-mando" onchange="renderScouts()">
                    <option value="total">Total</option><option value="casa">Casa</option><option value="fora">Fora</option>
                </select>
            </div>
        </div>
        <div id="scouts-list"></div>
    </div>
</div>
<script>
    // Limpador de cache
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(regs => { for(let r of regs) r.unregister(); });
    }

    const dadosScouts = __DADOS_SCOUTS__;
    const dadosTop5 = __DADOS_TOP5__;

    function openTab(tabId, event) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        if (event) event.target.classList.add('active');
    }

    function renderTop5() {
        const container = document.getElementById('top5-container');
        const posicoesNomes = { 'GOL': 'Goleiros', 'LAT': 'Laterais', 'ZAG': 'Zagueiros', 'MEI': 'Meias', 'ATA': 'Atacantes', 'TEC': 'Técnicos' };
        
        if (!dadosTop5 || Object.keys(dadosTop5).length === 0) {
            container.innerHTML = '<p class="erro-msg">Nenhum dado encontrado.</p>';
            return;
        }
        
        container.innerHTML = '';
        for (const [pos, jogadores] of Object.entries(dadosTop5)) {
            if (jogadores.length === 0) continue;
            let html = `<div class="top5-card"><h3>${posicoesNomes[pos] || pos}</h3>`;
            jogadores.forEach((j, index) => {
                html += `<p><span><strong>${index + 1}º</strong> ${j.nome} <small>(${j.clube})</small></span> <span style="color: var(--accent)">${j.media_ult5 ? j.media_ult5.toFixed(2) : '0.00'}</span></p>`;
            });
            html += `</div>`;
            container.innerHTML += html;
        }
    }

    function renderScouts() {
        try {
            const posicao = document.getElementById('filtro-posicao').value;
            const periodo = document.getElementById('filtro-periodo').value;
            const mando = document.getElementById('filtro-mando').value;
            const container = document.getElementById('scouts-list');
            
            // Define os scouts que vão aparecer em cada posição
            const scoutsPorPosicao = {
                'GOL': ['DE', 'SG', 'pontuacao'],
                'LAT': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'SG', 'pontuacao'],
                'ZAG': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'SG', 'pontuacao'],
                'MEI': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'pontuacao'],
                'ATA': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'pontuacao'],
                'TEC': ['pontuacao']
            };
            
            const nomesColunas = { 'DE': 'Defesas', 'SG': 'Saldo Gols', 'DS': 'Desarmes', 'FF': 'Fin. Fora', 'FD': 'Fin. Def', 'FT': 'Fin. Trave', 'G': 'Gols', 'A': 'Assistências', 'pontuacao': 'Média Pts' };
            const colunas = scoutsPorPosicao[posicao] || [];

            if (!dadosScouts || Object.keys(dadosScouts).length === 0) {
                container.innerHTML = '<p class="erro-msg">Nenhum dado encontrado. Rode a análise primeiro.</p>';
                return;
            }

            let jogadoresFiltrados = [];
            for (const [id, data] of Object.entries(dadosScouts)) {
                if (data.posicao !== posicao) continue;
                
                // Pega dados do período/mando (se existir, senão usa total)
                let dadosFinais = data[periodo];
                if (mando !== 'total' && data[mando]) { dadosFinais = data[mando]; }
                
                if (dadosFinais && dadosFinais.pontuacao !== undefined) {
                    jogadoresFiltrados.push({ nome: data.nome, clube: data.clube, dados: dadosFinais });
                }
            }

            // Ordena pelos que têm mais pontos
            jogadoresFiltrados.sort((a, b) => (b.dados.pontuacao || 0) - (a.dados.pontuacao || 0));

            // Pega o maior valor de scout para usar como base nas barras
            let maxValores = {};
            colunas.forEach(c => {
                maxValores[c] = Math.max(...jogadoresFiltrados.map(j => j.dados[c] || 0), 1);
            });

            let html = '';
            jogadoresFiltrados.slice(0, 20).forEach(j => { // Mostra o Top 20 da posição
                html += `<div class="scout-card">
                    <div class="scout-info">
                        <div class="scout-name">${j.nome}</div>
                        <div class="scout-club">${j.clube}</div>
                    </div>
                    <div class="scout-bars">`;
                
                colunas.forEach(c => {
                    if (c === 'pontuacao') return; // Mostra a pontuação no final
                    
                    const valor = j.dados[c] || 0;
                    const porcentagem = (valor / maxValores[c]) * 100;
                    
                    html += `<div class="bar-row">
                        <div class="bar-label">${nomesColunas[c]}</div>
                        <div class="bar-container">
                            <div class="bar-fill bar-green" style="width: ${porcentagem}%;">${valor > 0 ? valor : ''}</div>
                        </div>
                    </div>`;
                });
                
                html += `</div>
                    <div style="text-align: right; min-width: 80px;">
                        <div style="font-size: 0.8rem; color: #888;">Média Pts</div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: var(--accent);">${j.dados.pontuacao || 0}</div>
                    </div>
                </div>`;
            });
            
            container.innerHTML = html || '<p class="erro-msg">Nenhum jogador encontrado com esses filtros.</p>';
            
        } catch (e) { console.error(e); }
    }

    window.onload = function() { renderTop5(); renderScouts(); };
</script>
</body>
</html>
"""

    html_final = html_template.replace("__DADOS_SCOUTS__", js_analise).replace("__DADOS_TOP5__", js_top5)
    caminho_html = os.path.join(BASE_DIR, "index.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_final)
    print(f"✅ Site gerado em: {caminho_html}")
    
    try:
        subprocess.run(["git", "add", "index.html"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Atualização: Layout Visual de Scouts"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("✅ Site enviado para o GitHub!")
    except Exception as e:
        print(f"⚠️ Push falhou: {e}")

if __name__ == "__main__":
    gerar_html()
