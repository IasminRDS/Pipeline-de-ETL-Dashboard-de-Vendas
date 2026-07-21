"""
Testes do pipeline (transformação) e da camada de análise (SQL).
Rode com: python -m unittest -v
"""

import sqlite3
import unittest

import pandas as pd

import analise
import etl


class TestTransformacao(unittest.TestCase):
    def setUp(self):
        self.bruto = pd.DataFrame(
            {
                "data": ["2024-03-15", "2024-07-02"],
                "produto": ["  NOTEBOOK  ", "mouse"],
                "categoria": ["Eletronicos", "Acessorios"],
                "cidade": ["", "Salvador"],
                "regiao": ["Nordeste", "Nordeste"],
                "vendedor": ["Ana", "Bruno"],
                "quantidade": [2, 3],
                "preco_unitario": [4000.0, 100.0],
            }
        )
        self.tratado = etl.transformar(self.bruto)

    def test_normaliza_nome_produto(self):
        # "  NOTEBOOK  " -> "Notebook"
        self.assertEqual(self.tratado.loc[0, "produto"], "Notebook")

    def test_preenche_cidade_faltante(self):
        self.assertEqual(self.tratado.loc[0, "cidade"], "Não informada")

    def test_calcula_receita(self):
        self.assertAlmostEqual(self.tratado.loc[0, "receita"], 8000.0)
        self.assertAlmostEqual(self.tratado.loc[1, "receita"], 300.0)

    def test_cria_coluna_mes(self):
        self.assertEqual(self.tratado.loc[0, "mes"], 3)
        self.assertEqual(self.tratado.loc[0, "mes_nome"], "Mar")

    def test_remove_linhas_invalidas(self):
        bruto = self.bruto.copy()
        bruto.loc[0, "quantidade"] = 0  # inválida
        tratado = etl.transformar(bruto)
        self.assertEqual(len(tratado), 1)


class TestAnalise(unittest.TestCase):
    def setUp(self):
        # Banco em memória com dados controlados
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute(
            "CREATE TABLE vendas (produto TEXT, categoria TEXT, vendedor TEXT, "
            "quantidade INT, receita REAL, mes INT, mes_nome TEXT)"
        )
        linhas = [
            ("Notebook", "Eletronicos", "Ana", 2, 8000.0, 1, "Jan"),
            ("Mouse", "Acessorios", "Bruno", 5, 500.0, 1, "Jan"),
            ("Notebook", "Eletronicos", "Ana", 1, 4000.0, 2, "Fev"),
        ]
        self.con.executemany(
            "INSERT INTO vendas VALUES (?,?,?,?,?,?,?)", linhas
        )

    def tearDown(self):
        self.con.close()

    def test_kpis_gerais(self):
        kpis = analise.kpis_gerais(self.con)
        self.assertEqual(kpis["total_vendas"], 3)
        self.assertAlmostEqual(kpis["receita_total"], 12500.0)
        self.assertEqual(kpis["itens_vendidos"], 8)

    def test_receita_por_categoria_ordenada(self):
        cats = analise.receita_por_categoria(self.con)
        self.assertEqual(cats[0]["categoria"], "Eletronicos")
        self.assertAlmostEqual(cats[0]["receita"], 12000.0)

    def test_top_produtos(self):
        top = analise.top_produtos(self.con, limite=1)
        self.assertEqual(top[0]["produto"], "Notebook")
        self.assertEqual(top[0]["unidades"], 3)

    def test_ranking_vendedores(self):
        ranking = analise.ranking_vendedores(self.con)
        self.assertEqual(ranking[0]["vendedor"], "Ana")


if __name__ == "__main__":
    unittest.main()
