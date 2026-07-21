"""
Análise dos dados de vendas usando SQL sobre o banco gerado pelo ETL.
Cada indicador é uma consulta SQL isolada (fácil de reaproveitar e testar).

Uso:
    python analise.py      (rode 'python etl.py' antes)
"""

import sqlite3

BANCO = "vendas.db"


def conectar(banco=BANCO):
    conexao = sqlite3.connect(banco)
    conexao.row_factory = sqlite3.Row
    return conexao


# ---------- Indicadores (cada um é uma consulta SQL) ----------
def kpis_gerais(con):
    sql = """
        SELECT
            COUNT(*)                AS total_vendas,
            SUM(receita)            AS receita_total,
            AVG(receita)            AS ticket_medio,
            SUM(quantidade)         AS itens_vendidos
        FROM vendas
    """
    return dict(con.execute(sql).fetchone())


def receita_por_categoria(con):
    sql = """
        SELECT categoria, ROUND(SUM(receita), 2) AS receita
        FROM vendas
        GROUP BY categoria
        ORDER BY receita DESC
    """
    return [dict(r) for r in con.execute(sql).fetchall()]


def receita_por_mes(con):
    sql = """
        SELECT mes, mes_nome, ROUND(SUM(receita), 2) AS receita
        FROM vendas
        GROUP BY mes, mes_nome
        ORDER BY mes
    """
    return [dict(r) for r in con.execute(sql).fetchall()]


def top_produtos(con, limite=5):
    sql = """
        SELECT produto,
               SUM(quantidade)      AS unidades,
               ROUND(SUM(receita), 2) AS receita
        FROM vendas
        GROUP BY produto
        ORDER BY receita DESC
        LIMIT ?
    """
    return [dict(r) for r in con.execute(sql, (limite,)).fetchall()]


def ranking_vendedores(con):
    sql = """
        SELECT vendedor, ROUND(SUM(receita), 2) AS receita
        FROM vendas
        GROUP BY vendedor
        ORDER BY receita DESC
    """
    return [dict(r) for r in con.execute(sql).fetchall()]


# ---------- Relatório no terminal ----------
def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def imprimir_relatorio():
    con = conectar()
    try:
        kpis = kpis_gerais(con)
        print("=" * 42)
        print("  RELATORIO DE VENDAS")
        print("=" * 42)
        print(f"  Receita total....: {brl(kpis['receita_total'])}")
        print(f"  Total de vendas..: {kpis['total_vendas']}")
        print(f"  Itens vendidos...: {kpis['itens_vendidos']}")
        print(f"  Ticket medio.....: {brl(kpis['ticket_medio'])}")

        print("\n  Receita por categoria:")
        for r in receita_por_categoria(con):
            print(f"    - {r['categoria']:<12} {brl(r['receita'])}")

        print("\n  Top 5 produtos:")
        for i, r in enumerate(top_produtos(con), 1):
            print(f"    {i}. {r['produto']:<16} {brl(r['receita'])} ({r['unidades']} un.)")

        print("\n  Ranking de vendedores:")
        for i, r in enumerate(ranking_vendedores(con), 1):
            print(f"    {i}. {r['vendedor']:<8} {brl(r['receita'])}")
        print("=" * 42)
    finally:
        con.close()


if __name__ == "__main__":
    imprimir_relatorio()
