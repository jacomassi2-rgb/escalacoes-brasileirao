# ⚽ Prováveis Escalações - Brasileirão Série A

Plataforma completa de análise para o Cartola FC: notícias, classificação, parciais ao vivo e o seu time — tudo em um só lugar, atualizado automaticamente.

**🌐 Site online:** [jacomassi2-rgb.github.io/escalacoes-brasileirao](https://jacomassi2-rgb.github.io/escalacoes-brasileirao)

---

## ✨ Funcionalidades

### 📰 Notícias
- Coleta automática de notícias sobre prováveis escalações dos 20 times via Google News
- Busca por time em tempo real
- Filtro "últimas 24h"
- Botão "Ver escalação" que abre a notícia mais relevante
- Tempo relativo em cada notícia ("há 2h", "há 1 dia")

### 🏆 Classificação
- Tabela completa do Brasileirão via API football-data.org
- Top 4 destacado (Libertadores), G5-G8 (Pré-Libertadores), Z4 (Rebaixamento)
- Atualizada automaticamente

### 👤 Meu Time
- Cadastro manual do seu time no `meu_time.json`
- Pontuação de cada jogador
- Capitão com bônus ×1.5
- Comparador automático com a sugestão do Fathur FC
- Barra de "acordo" mostrando quantos jogadores você tem em comum

### 🔴 Parciais ao Vivo
- Pontuação em tempo real de **todos os jogadores** de **todos os jogos**
- Agrupadas por partida (Time A x Time B)
- Placar total de cada time
- Jogadores separados por posição (GOL, LAT, ZAG, MEI, ATA, TEC)
- Scouts individuais (gols, assistências, desarmes, etc.)
- Atualização a cada 10 minutos durante os jogos

### 📱 Notificações Telegram
- Resumo diário 3x ao dia (8h, 13h, 18h)
- Alertas em tempo real de mudanças de pontuação durante os jogos

---

## 🛠️ Arquitetura

| Componente | Função |
|---|---|
| `coletor.py` | Coleta notícias do Google News e salva no SQLite |
| `gerar_site.py` | Monta o `index.html` com todas as abas |
| `config.py` | Busca rodada, jogos e classificação via API |
| `notificador.py` | Envia notificação no Telegram quando o site atualiza |
| `parciais.py` | Busca parciais do Cartola e notifica mudanças |
| `atualizar_site_parciais.py` | Injeta as parciais no `index.html` |

### Workflows do GitHub Actions

| Workflow | Frequência | Função |
|---|---|---|
| `atualizar.yml` | 3x ao dia | Coleta notícias, gera site, envia Telegram |
| `pontuacao.yml` | A cada 10 min (durante jogos) | Busca parciais e notifica mudanças |

### APIs usadas

- **football-data.org** — rodada, jogos e classificação
- **Cartola FC** — parciais dos jogadores
- **Google News RSS** — notícias sobre escalações
- **Logo.dev** — escudos dos times
- **Telegram Bot API** — notificações

---

## 🔄 Manutenção

### Atualizar o `meu_time.json` (antes de cada rodada)

```json
{
  "rodada": 32,
  "jogadores": [
    {"nome": "Rossi", "clube": "FLA", "posicao": "GOL", "pontos": 0, "capitao": false},
    {"nome": "Hulk", "clube": "FLU", "posicao": "ATA", "pontos": 0, "capitao": true}
  ]
}
