# ⚽ Prováveis Escalações - Brasileirão Série A

Agregador automático de notícias sobre prováveis escalações dos 20 times da Série A do Brasileirão.

**🌐 Site online:** [jacomassi2-rgb.github.io/escalacoes-brasileirao](https://jacomassi2-rgb.github.io/escalacoes-brasileirao)

---

## ✨ Funcionalidades

- 📰 **Coleta automática** de notícias de 20 times via Google News
- 🤖 **Atualização 3x ao dia** (8h, 13h, 18h - horário de Brasília)
- 🔘 **Botão manual** pra forçar atualização a qualquer momento
- 🔍 **Busca por time** em tempo real
- 🕐 **Filtro "últimas 24h"**
- 🏆 **Rodada atual + 10 jogos** da rodada
- 🖼️ **Escudos dos times** (via Logo.dev)
- 🟢 **Botão "Ver escalação"** que abre a notícia mais relevante
- ⏱️ **Tempo relativo** em cada notícia ("há 2h", "há 1 dia")
- 🌙 **Tema claro/escuro** (com preferência salva)
- 📱 **Notificação no Telegram** a cada atualização
- ⬆️ **Botão voltar ao topo**

---

## 🛠️ Como funciona

O sistema roda 100% no **GitHub Actions** (gratuito) e usa:

| Componente | Função |
|---|---|
| `coletor.py` | Busca notícias no Google News e salva no SQLite |
| `gerar_site.py` | Monta o `index.html` com as notícias |
| `config.py` | Configurações (rodada atual, jogos, dados manuais) |
| `.github/workflows/atualizar.yml` | Agendador que roda o robô 3x/dia |
| `index.html` | Site gerado (publicado automaticamente pelo GitHub Pages) |

---

## 🔄 Como atualizar a rodada (manual — 1x por semana)

Quando o Brasileirão avançar para a próxima rodada:

1. Acesse o arquivo **`config.py`** no GitHub
2. Clique no ícone de **lápis ✏️** (editar)
3. Altere as 3 variáveis:
   - `RODADA_ATUAL` → número da nova rodada (ex: `30`)
   - `DATA_RODADA` → datas dos jogos (ex: `"15 e 16 de outubro de 2026"`)
   - `JOGOS_RODADA` → lista com os 10 jogos da rodada
4. Clique em **"Commit changes"** → confirmar
5. Vá em **Ações** → **Atualizar Escalações** → **Executar fluxo de trabalho**

Pronto! O site vai atualizar em 1-2 minutos.

---

## 🤖 Como forçar uma atualização manual

1. Acesse a aba **Ações** do repositório
2. Clique em **"Atualizar Escalações"** (lateral esquerda)
3. Clique no botão **"Executar fluxo de trabalho"** (canto superior direito)
4. Confirme no botão verde
5. Aguarde ~40 segundos

---

## 🔔 Notificações no Telegram

Toda vez que o robô roda, você recebe uma mensagem no Telegram com:
- Rodada atual
- Hora da atualização
- Link do site

**Como está configurado:**
- Bot: `@meu_robo_escalacoes_bot`
- Secrets no GitHub: `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`

---

## ⚙️ Configuração inicial (caso precise recriar)

### 1. Secrets necessários no GitHub

Vá em **Configurações** → **Segredos e variáveis** → **Ações** e crie:

| Nome | Valor |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token do bot do Telegram (@BotFather) |
| `TELEGRAM_CHAT_ID` | Seu chat ID do Telegram |
| `FOOTBALL_DATA_TOKEN` | Token do football-data.org (opcional, atualmente não usado) |

### 2. Ativar GitHub Pages

Vá em **Configurações** → **Páginas**:
- **Fonte:** Implantar a partir de uma ramificação
- **Filial:** `main` / `(raiz)`
- Salvar

---

## 🐛 Problemas conhecidos

| Problema | Solução |
|---|---|
| Site desatualizado | Apertar **Ctrl+F5** ou abrir em **janela anônima** |
| Escudo não aparece | Aguardar 1-2 min (cache do GitHub Pages) |
| Notificação não chega | Verificar se os secrets do Telegram estão certos |
| Rodada errada | Editar `config.py` manualmente |

---

## 📝 Como o site é gerado
