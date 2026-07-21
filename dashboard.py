"""
Gera um dashboard HTML interativo (dashboard.html) a partir do banco de vendas.
Os gráficos são desenhados em SVG puro — o arquivo é 100% autossuficiente,
abre em qualquer navegador e pode ser publicado no GitHub Pages.

Uso:
    python dashboard.py    (rode 'python etl.py' antes)
"""

import analise

SAIDA = "dashboard.html"
COR = "#2563eb"
COR2 = "#7c3aed"


def brl_curto(v):
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v/1_000:.0f}k"
    return f"R$ {v:.0f}"


def cartao_kpi(titulo, valor):
    return f"""
    <div class="kpi">
      <span class="kpi-titulo">{titulo}</span>
      <strong class="kpi-valor">{valor}</strong>
    </div>"""


def barras_verticais(dados, chave_rotulo, chave_valor, largura=560, altura=240):
    """Gráfico de barras verticais em SVG."""
    if not dados:
        return ""
    valores = [d[chave_valor] for d in dados]
    maximo = max(valores) or 1
    n = len(dados)
    margem = 30
    area_alt = altura - margem - 20
    espaco = (largura - margem) / n
    barra_l = espaco * 0.6

    barras = []
    for i, d in enumerate(dados):
        h = area_alt * (d[chave_valor] / maximo)
        x = margem + i * espaco + (espaco - barra_l) / 2
        y = altura - 20 - h
        barras.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{barra_l:.1f}" height="{h:.1f}" '
            f'rx="4" fill="{COR}"><title>{d[chave_rotulo]}: {brl_curto(d[chave_valor])}</title></rect>'
            f'<text x="{x + barra_l/2:.1f}" y="{altura-6}" font-size="10" '
            f'fill="#64748b" text-anchor="middle">{d[chave_rotulo]}</text>'
        )
    return f'<svg viewBox="0 0 {largura} {altura}" class="grafico">{"".join(barras)}</svg>'


def barras_horizontais(dados, chave_rotulo, chave_valor, largura=560):
    """Gráfico de barras horizontais (ranking) em SVG."""
    if not dados:
        return ""
    maximo = max(d[chave_valor] for d in dados) or 1
    linha_alt = 34
    altura = linha_alt * len(dados) + 10
    rotulo_l = 130
    barra_area = largura - rotulo_l - 70

    linhas = []
    for i, d in enumerate(dados):
        y = i * linha_alt + 8
        w = barra_area * (d[chave_valor] / maximo)
        linhas.append(
            f'<text x="0" y="{y+16}" font-size="12" fill="#334155">{d[chave_rotulo]}</text>'
            f'<rect x="{rotulo_l}" y="{y+4}" width="{w:.1f}" height="18" rx="4" fill="{COR2}"/>'
            f'<text x="{rotulo_l + w + 6:.1f}" y="{y+18}" font-size="11" '
            f'fill="#64748b">{brl_curto(d[chave_valor])}</text>'
        )
    return f'<svg viewBox="0 0 {largura} {altura}" class="grafico">{"".join(linhas)}</svg>'


def gerar(saida=SAIDA):
    con = analise.conectar()
    try:
        kpis = analise.kpis_gerais(con)
        por_mes = analise.receita_por_mes(con)
        por_categoria = analise.receita_por_categoria(con)
        top = analise.top_produtos(con)
        vendedores = analise.ranking_vendedores(con)
    finally:
        con.close()

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard de Vendas</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; font-family:"Segoe UI",system-ui,sans-serif; }}
  body {{ background:#f1f5f9; color:#0f172a; padding:32px 20px; }}
  .container {{ max-width:1100px; margin:0 auto; }}
  h1 {{ font-size:26px; margin-bottom:4px; }}
  .subtitulo {{ color:#64748b; margin-bottom:24px; font-size:14px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
  .kpi {{ background:#fff; border-radius:14px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,.08); border-left:4px solid {COR}; }}
  .kpi-titulo {{ display:block; color:#64748b; font-size:13px; margin-bottom:6px; }}
  .kpi-valor {{ font-size:24px; color:#0f172a; }}
  .paineis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:16px; }}
  .painel {{ background:#fff; border-radius:14px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  .painel h2 {{ font-size:15px; margin-bottom:14px; color:#334155; }}
  .grafico {{ width:100%; height:auto; }}
  footer {{ text-align:center; color:#94a3b8; font-size:12px; margin-top:28px; }}
</style>
</head>
<body>
  <div class="container">
    <h1>📊 Dashboard de Vendas</h1>
    <p class="subtitulo">Gerado automaticamente pelo pipeline de dados · fonte: vendas.db</p>

    <div class="kpis">
      {cartao_kpi("Receita total", brl_curto(kpis['receita_total']))}
      {cartao_kpi("Total de vendas", str(kpis['total_vendas']))}
      {cartao_kpi("Itens vendidos", str(kpis['itens_vendidos']))}
      {cartao_kpi("Ticket médio", brl_curto(kpis['ticket_medio']))}
    </div>

    <div class="paineis">
      <div class="painel">
        <h2>Receita por mês</h2>
        {barras_verticais(por_mes, "mes_nome", "receita")}
      </div>
      <div class="painel">
        <h2>Receita por categoria</h2>
        {barras_verticais(por_categoria, "categoria", "receita")}
      </div>
      <div class="painel">
        <h2>Top 5 produtos</h2>
        {barras_horizontais(top, "produto", "receita")}
      </div>
      <div class="painel">
        <h2>Ranking de vendedores</h2>
        {barras_horizontais(vendedores, "vendedor", "receita")}
      </div>
    </div>

    <footer>Pipeline ETL + Dashboard · Python + SQLite · dados fictícios de demonstração</footer>
  </div>
</body>
</html>"""

    with open(saida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK - Dashboard gerado: {saida}")


if __name__ == "__main__":
    gerar()
