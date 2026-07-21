"""
Gera um dataset de vendas fictício (dados/vendas.csv) para o pipeline.
Os dados são sintéticos e servem apenas de exemplo — inclui, de propósito,
alguns problemas de qualidade (espaços, capitalização, campos vazios) para
que a etapa de transformação do ETL tenha o que limpar.
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)  # reprodutível

PRODUTOS = [
    ("Notebook", "Eletronicos", 3200, 5000),
    ("Smartphone", "Eletronicos", 1500, 4000),
    ("Monitor", "Eletronicos", 800, 2200),
    ("Fone de Ouvido", "Acessorios", 80, 600),
    ("Mouse", "Acessorios", 40, 250),
    ("Teclado", "Acessorios", 90, 400),
    ("Webcam", "Acessorios", 120, 500),
    ("Cadeira Gamer", "Escritorio", 700, 1800),
    ("Mesa", "Escritorio", 400, 1200),
    ("Luminaria", "Escritorio", 60, 300),
]

CIDADES = [
    ("Salvador", "Nordeste"),
    ("Bom Jesus da Lapa", "Nordeste"),
    ("Feira de Santana", "Nordeste"),
    ("Vitoria da Conquista", "Nordeste"),
    ("Sao Paulo", "Sudeste"),
    ("Rio de Janeiro", "Sudeste"),
    ("Curitiba", "Sul"),
]

VENDEDORES = ["Ana", "Bruno", "Carla", "Diego", "Elaine", "Fabio"]


def gerar(qtd=280, caminho="dados/vendas.csv"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    inicio = date(2024, 1, 1)

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(
            ["data", "produto", "categoria", "cidade", "regiao",
             "vendedor", "quantidade", "preco_unitario"]
        )

        for _ in range(qtd):
            produto, categoria, pmin, pmax = random.choice(PRODUTOS)
            cidade, regiao = random.choice(CIDADES)
            dia = inicio + timedelta(days=random.randint(0, 364))
            quantidade = random.randint(1, 8)
            preco = round(random.uniform(pmin, pmax), 2)

            # Ruído proposital para o ETL limpar depois:
            if random.random() < 0.10:
                produto = f"  {produto.upper()}  "        # espaços + caixa alta
            if random.random() < 0.05:
                cidade = ""                                # cidade faltando

            escritor.writerow(
                [dia.isoformat(), produto, categoria, cidade, regiao,
                 random.choice(VENDEDORES), quantidade, preco]
            )

    print(f"Gerado: {caminho} ({qtd} linhas)")


if __name__ == "__main__":
    gerar()
