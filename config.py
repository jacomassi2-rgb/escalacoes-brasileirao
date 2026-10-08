# ==============================================
# CONFIGURAÇÕES DO SITE
# ==============================================
# Atualize este arquivo quando mudar a rodada
# ==============================================

RODADA_ATUAL = 29
DATA_RODADA = "08 e 09 de outubro de 2026"

# Jogos da rodada 29
# Formato: ("Time Casa", "Time Visitante", "Dia HH:MM")
JOGOS_RODADA = [
    ("Internacional", "Corinthians", "08/10 19:00"),
    ("Remo", "Grêmio", "08/10 18:00"),
    ("Bragantino", "Mirassol", "08/10 20:30"),
    ("Vitória", "Chapecoense", "08/10 16:00"),
    ("Botafogo", "Vasco", "08/10 21:30"),
    ("Cruzeiro", "São Paulo", "08/10 17:00"),
    ("Santos", "Flamengo", "08/10 21:30"),
    ("Athletico Paranaense", "Atlético Mineiro", "08/10 18:30"),
    ("Palmeiras", "Bahia", "08/10 19:00"),
    ("Fluminense", "Coritiba", "08/10 20:00"),
]

def obter_rodada_e_jogos():
    return RODADA_ATUAL, DATA_RODADA, JOGOS_RODADA
