import os
if os.path.exists('dados/escalacoes.db'):
    os.remove('dados/escalacoes.db')
    print("Banco apagado!")
else:
    print("Banco não existia.")
