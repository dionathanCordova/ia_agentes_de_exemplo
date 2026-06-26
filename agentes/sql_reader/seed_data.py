import random
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker

N = 1000
ESTADOS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]
TIPOS_MOVIMENTACAO = ["deposito", "retirada", "transferencia", "pix", "boleto"]

faker = Faker("pt_BR")

conn = mysql.connector.connect(
    host="localhost",
    password="agente123",
    port=3306,
    user="agente",
    database="agentes_db",
)
cursor = conn.cursor()


def random_datetime(days_back=730):
    delta = timedelta(days=random.randint(0, days_back), seconds=random.randint(0, 86400))
    return datetime.now() - delta


clientes = [
    (faker.unique.cpf(), faker.name(), faker.unique.email())
    for _ in range(N)
]
cursor.executemany(
    "INSERT INTO clientes (cpf, nome, email) VALUES (%s, %s, %s)",
    clientes,
)
conn.commit()

cursor.execute("SELECT cliente_id FROM clientes")
cliente_ids = [row[0] for row in cursor.fetchall()]

enderecos = [
    (random.choice(cliente_ids), faker.street_name(), faker.city(), random.choice(ESTADOS), faker.postcode())
    for _ in range(N)
]
cursor.executemany(
    "INSERT INTO enderecos (cliente_id, rua, cidade, estado, cep) VALUES (%s, %s, %s, %s, %s)",
    enderecos,
)
conn.commit()

movimentacoes = [
    (
        random.choice(cliente_ids),
        random.choice(TIPOS_MOVIMENTACAO),
        round(random.uniform(10, 50000), 2),
        random_datetime(),
    )
    for _ in range(N)
]
cursor.executemany(
    "INSERT INTO movimentacoes (cliente_id, tipo_movimentacao, valor, data_movimentacao) VALUES (%s, %s, %s, %s)",
    movimentacoes,
)
conn.commit()

pagamentos = [
    (random.choice(cliente_ids), round(random.uniform(10, 50000), 2), random_datetime())
    for _ in range(N)
]
cursor.executemany(
    "INSERT INTO pagamentos (cliente_id, valor, data_pagamento) VALUES (%s, %s, %s)",
    pagamentos,
)
conn.commit()

print(f"clientes: {len(clientes)}")
print(f"enderecos: {len(enderecos)}")
print(f"movimentacoes: {len(movimentacoes)}")
print(f"pagamentos: {len(pagamentos)}")

cursor.close()
conn.close()
