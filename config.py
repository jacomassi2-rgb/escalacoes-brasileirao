# ==============================================
# CONFIGURAÇÕES DO SITE
# ==============================================
# Atualize este arquivo quando mudar a rodada
# ==============================================

RODADA_ATUAL = 29
DATA_RODADA = "08 e 09 de outubro de 2026"

# Jogos da rodada
# Formato: ("Time Casa", "Time Visitante", "Dia HH:MM")
JOGOS_RODADA = [
    ("Flamengo", "Santos", "08/10 21:30"),
    ("Palmeiras", "Bahia", "08/10 19:00"),
    ("Corinthians", "Bragantino", "08/10 18:30"),
    ("São Paulo", "Mirassol", "08/10 16:00"),
    ("Botafogo", "Fluminense", "08/10 20:00"),
    ("Vasco", "Grêmio", "08/10 21:30"),
    ("Internacional", "Cruzeiro", "08/10 17:00"),
    ("Atlético Mineiro", "Vitória", "08/10 18:00"),
    ("Fortaleza", "Ceará", "08/10 19:00"),
    ("Sport", "Juventude", "08/10 16:30"),
]

# Função que o gerar_site.py chama (mantém compatibilidade)
def obter_rodada_e_jogos():
    return RODADA_ATUAL, DATA_RODADA, JOGOS_RODADA
