# ============================================================
# SCRIPT COMPLETO: gerar_site.py
# Lê os JSONs gerados e monta o index.html completo
# ============================================================
import os
import json

BASE_DIR = "/content/drive/MyDrive/fathur_fc"

def carregar_json(nome_arquivo):
    caminho = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def gerar_html():
    analise_scouts = carregar_json("analise_scouts.json")
    top5_posicoes = carregar_json("top5_posicoes.json")
    
    # Transforma os dicionários em strings JSON seguras para injetar no JS
    js_analise = json.dumps(analise_scouts, ensure_ascii=False)
    js_top5 = json.dumps(top5_posicoes, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fathur FC — Análise Cartola</title>
    <style>
        :root {{
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --accent: #00b894;
            --accent-hover: #00a884;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }}
        header {{
            background-color: #000;
            padding: 15px 20px;
            text-align: center;
            border-bottom: 2px solid var(--accent);
        }}
        header h1 {{ margin: 0; font-size: 1.5rem; }}
        .tabs {{
            display: flex;
            background-color: #000;
            justify-content: center;
            gap: 10px;
            padding: 10px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            color: #888;
            padding: 10px 20px;
            font-size: 1rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: 0.3s;
        }}
        .tab-btn.active {{
            color: var(--accent);
            border-bottom: 2px solid var(--accent);
            font-weight: bold;
        }}
        .container {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        /* Estilos para a Tabela de Scouts */
        .filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 8px;
        }}
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        .filter-group label {{
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 5px;
        }}
        .filter-group select {{
            background-color: #333;
            color: white;
            border: 1px solid #555;
            padding: 8px;
            border-radius: 4px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            background-color: #2c2c2c;
            color: var(--accent);
            font-weight: 600;
        }}
        tr:hover {{ background-color: #2a2a2a; }}
        
        /* Estilos para os Cards Top 5 */
        .top5-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        .top5-card {{
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
        }}
        .top5-card h3 {{ margin: 0 0 10px 0; font-size: 1rem; color: var(--accent); }}
        .top5-card p {{ margin: 5px 0; font-size: 0.9rem; }}
        
        /* Estilos para Classificação */
        #classificacao-container {{
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .live-badge {{
            background-color: red;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            animation: blink 1s infinite;
        }}
        @keyframes blink {{ 50% {{ opacity: 0; }} }}
    </style>
</head>
<body>

<header>
    <h1>⚽ Fathur FC — Análise e Estratégia</h1>
</header>

<div class="tabs">
    <button class="tab-btn active" onclick="openTab('classificacao')">🏆 Classificação</button>
    <button class="tab-btn" onclick="openTab('top5')">⭐ Top 5 Posições</button>
    <button class="tab-btn" onclick="openTab('scouts')">📊 Cruzamento de Scouts</button>
</div>

<div class="container">
    <!-- ABA CLASSIFICAÇÃO -->
    <div id="classificacao" class="tab-content active">
        <div id="classificacao-container">
            <h2>Campeonato Brasileiro 2026 <span class="live-badge">AO VIVO</span></h2>
            <p style="color: #888;">A classificação está sendo carregada em tempo real...</p>
            <!-- Aqui entraria a API de classificação. Como não podemos garantir a API pública, 
                 deixamos a estrutura pronta para você plugar o iframe ou JS da API do Cartola -->
            <div id="tabela-classificacao">
                <p><em>[Aqui será carregado o iframe/API de classificação]</em></p>
            </div>
        </div>
    </div>

    <!-- ABA TOP 5 -->
    <div id="top5" class="tab-content">
        <h2>Top 5 Melhores Opções (Últimos 5 jogos)</h2>
        <div id="top5-container" class="top5-container">
            <!-- Preenchido via JS -->
        </div>
    </div>

    <!-- ABA SCOUTS -->
    <div id="scouts" class="tab-content">
        <h2>Cruzamento de Scouts por Posição</h2>
        
        <div class="filters">
            <div class="filter-group">
                <label>Posição</label>
                <select id="filtro-posicao" onchange="renderScouts()">
                    <option value="GOL">Goleiros</option>
                    <option value="LAT">Laterais</option>
                    <option value="ZAG">Zagueiros</option>
                    <option value="MEI">Meias</option>
                    <option value="ATA">Atacantes</option>
                    <option value="TEC">Técnicos</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Período</label>
                <select id="filtro-periodo" onchange="renderScouts()">
                    <option value="ultimos_3">Últimos 3 jogos</option>
                    <option value="ultimos_5">Últimos 5 jogos</option>
                    <option value="total">Total (Histórico)</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Mando de Campo</label>
                <select id="filtro-mando" onchange="renderScouts()">
                    <option value="total">Total</option>
                    <option value="casa">Casa</option>
                    <option value="fora">Fora</option>
                </select>
            </div>
        </div>

        <table>
            <thead id="scouts-thead">
                <!-- Preenchido via JS -->
            </thead>
            <tbody id="scouts-tbody">
                <!-- Preenchido via JS -->
            </tbody>
        </table>
    </div>
</div>

<script>
    // Dados injetados pelo Python
    const dadosScouts = {js_analise};
    const dadosTop5 = {js_top5};

    function openTab(tabId) {{
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        event.target.classList.add('active');
    }}

    // ================= ABA TOP 5 =================
    function renderTop5() {{
        const container = document.getElementById('top5-container');
        container.innerHTML = '';
        
        const posicoesNomes = {{
            'GOL': 'Goleiros', 'LAT': 'Laterais', 'ZAG': 'Zagueiros',
            'MEI': 'Meias', 'ATA': 'Atacantes', 'TEC': 'Técnicos'
        }};

        for (const [pos, jogadores] of Object.entries(dadosTop5)) {{
            if (jogadores.length === 0) continue;
            
            let html = `<div class="top5-card"><h3>${{posicoesNomes[pos] || pos}}</h3>`;
            jogadores.forEach((j, index) => {{
                html += `<p><strong>${{index + 1}}º</strong> ${{j.nome}} (${{j.clube}}) - <span style="color: var(--accent)">${{j.media_ult5.toFixed(2)}} pts</span></p>`;
            }});
            html += `</div>`;
            container.innerHTML += html;
        }}
    }}

    // ================= ABA SCOUTS =================
    function renderScouts() {{
        const posicao = document.getElementById('filtro-posicao').value;
        const periodo = document.getElementById('filtro-periodo').value;
        const mando = document.getElementById('filtro-mando').value;
        
        const thead = document.getElementById('scouts-thead');
        const tbody = document.getElementById('scouts-tbody');
        
        // Define quais scouts mostrar para cada posição
        const scoutsPorPosicao = {{
            'GOL': ['DE', 'SG', 'pontuacao'],
            'LAT': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'SG', 'pontuacao'],
            'ZAG': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'SG', 'pontuacao'],
            'MEI': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'pontuacao'],
            'ATA': ['DS', 'FF', 'FD', 'FT', 'G', 'A', 'pontuacao'],
            'TEC': ['pontuacao']
        }};
        
        const colunas = scoutsPorPosicao[posicao] || [];
        const nomesColunas = {{
            'DE': 'Defesas', 'SG': 'Saldo Gols', 'DS': 'Desarmes', 
            'FF': 'Finalizações Fora', 'FD': 'Finalizações Defendidas', 
            'FT': 'Finalizações Trave', 'G': 'Gols', 'A': 'Assistências', 
            'pontuacao': 'Pontuação'
        }};

        // Monta o Cabeçalho
        let headerHtml = '<tr><th>Jogador</th><th>Clube</th>';
        colunas.forEach(c => {{
            headerHtml += `<th>${{nomesColunas[c] || c}}</th>`;
        }});
        headerHtml += '</tr>';
        thead.innerHTML = headerHtml;

        // Filtra e ordena os jogadores
        let jogadoresFiltrados = [];
        for (const [id, data] of Object.entries(dadosScouts)) {{
            if (data.posicao !== posicao) continue;
            
            // Pega os dados do período e mando selecionados
            let dadosPeriodo = data[periodo];
            if (mando !== 'total' && dadosPeriodo) {{
                // Se o mando for diferente de total, cruza os dados do período com o mando
                // (Ex: ultimos_5 e casa -> aqui teríamos que ter os dados cruzados, mas 
                // para simplificar, usaremos a média do mando se existir)
                if (data[mando]) {{
                    dadosPeriodo = data[mando]; // fallback para a média geral de casa/fora
                }}
            }}
            
            if (dadosPeriodo && dadosPeriodo.pontuacao !== undefined) {{
                jogadoresFiltrados.push({{
                    nome: data.nome,
                    clube: data.clube,
                    dados: dadosPeriodo
                }});
            }}
        }}

        // Ordena por pontuação (decrescente)
        jogadoresFiltrados.sort((a, b) => (b.dados.pontuacao || 0) - (a.dados.pontuacao || 0));

        // Monta as Linhas
        let bodyHtml = '';
        jogadoresFiltrados.forEach(j => {{
            bodyHtml += `<tr><td>${{j.nome}}</td><td>${{j.clube}}</td>`;
            colunas.forEach(c => {{
                const valor = j.dados[c] !== undefined ? j.dados[c] : '-';
                bodyHtml += `<td>${{valor}}</td>`;
            }});
            bodyHtml += '</tr>';
        }});
        tbody.innerHTML = bodyHtml;
    }}

    // Inicializa as abas ao carregar a página
    window.onload = function() {{
        renderTop5();
        renderScouts();
    }};
</script>

</body>
</html>
"""
    
    # Salva o arquivo index.html na raiz do projeto
    caminho_html = os.path.join(BASE_DIR, "index.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Site gerado com sucesso em: {caminho_html}")
    
    # Tenta fazer o push para o GitHub
    try:
        import subprocess
        subprocess.run(["git", "add", "index.html"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Atualização do site: Scouts e Top 5"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("✅ Site enviado para o GitHub com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Push automático falhou. Envie o index.html manualmente. Erro: {e}")

if __name__ == "__main__":
    gerar_html()
