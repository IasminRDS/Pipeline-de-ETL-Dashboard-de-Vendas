"""
Pipeline ETL de vendas.

    Extract  -> lê o CSV bruto
    Transform-> limpa e enriquece os dados
    Load     -> grava em um banco SQLite pronto para análise

Uso:
    python etl.py
"""

import sqlite3

import pandas as pd

CSV_ENTRADA = "dados/vendas.csv"
BANCO = "vendas.db"
TABELA = "vendas"

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def extrair(caminho=CSV_ENTRADA):
    """Extract: carrega o CSV bruto em um DataFrame."""
    return pd.read_csv(caminho)


def transformar(df):
    """Transform: limpa e enriquece os dados."""
    df = df.copy()

    # 1. Padroniza texto (remove espaços e corrige a capitalização)
    df["produto"] = df["produto"].astype(str).str.strip().str.title()
    df["categoria"] = df["categoria"].str.strip().str.title()

    # 2. Preenche cidades faltantes
    df["cidade"] = df["cidade"].fillna("").str.strip()
    df.loc[df["cidade"] == "", "cidade"] = "Não informada"

    # 3. Tipos corretos
    df["data"] = pd.to_datetime(df["data"])
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    # 4. Colunas derivadas (enriquecimento)
    df["receita"] = (df["quantidade"] * df["preco_unitario"]).round(2)
    df["mes"] = df["data"].dt.month
    df["mes_nome"] = df["mes"].map(MESES_PT)
    df["data"] = df["data"].dt.strftime("%Y-%m-%d")

    # 5. Remove linhas impossíveis (qualidade de dados)
    df = df[(df["quantidade"] > 0) & (df["preco_unitario"] > 0)]

    return df.reset_index(drop=True)


def carregar(df, banco=BANCO, tabela=TABELA):
    """Load: grava o DataFrame tratado no SQLite."""
    with sqlite3.connect(banco) as conexao:
        df.to_sql(tabela, conexao, if_exists="replace", index=False)
    return len(df)


def executar_pipeline():
    print("[1/3] Extract: lendo", CSV_ENTRADA)
    bruto = extrair()
    print(f"  {len(bruto)} linhas lidas.")

    print("[2/3] Transform: limpando e enriquecendo...")
    tratado = transformar(bruto)
    print(f"  {len(tratado)} linhas válidas após a limpeza.")

    print("[3/3] Load: gravando em", BANCO)
    total = carregar(tratado)
    print(f"OK - Pipeline concluido: {total} registros na tabela '{TABELA}'.")
    return tratado


if __name__ == "__main__":
    executar_pipeline()
