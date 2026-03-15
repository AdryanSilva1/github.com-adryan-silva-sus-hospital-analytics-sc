import plotly.express as px
import pandas as pd

_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#c5e1ea",
)

_GRID = dict(
    gridcolor="#1e3a5f",
    showline=False,
)

_HOVER = dict(
    hoverlabel=dict(
        bgcolor="#0b1220",
        font_size=13,
        font_family="Roboto",
        bordercolor="#1e3a5f",
    )
)

# Remove a barra de ferramentas do Plotly em todos os gráficos
# Zoom, pan, câmera etc. são inúteis num dashboard de dados públicos
_CONFIG = {"displayModeBar": False}


def create_ranking(df_vis, municipio):
    """Top 15 ou município filtrado — sempre recebe df já filtrado."""

    if municipio == "Todos os municípios":
        df_r   = df_vis.head(15).copy()
        titulo = "Top 15 Municípios – Total de AIH"
    else:
        df_r   = df_vis.copy()
        titulo = municipio

    emojis = ["🥇 ", "🥈 ", "🥉 "] + [""] * max(0, len(df_r) - 3)
    rotulos = []
    for e, n in zip(emojis, df_r["municipio"]):
        rotulos.append(f"{e}{n}")
    df_r["rotulo"] = rotulos

    fig = px.bar(
        df_r,
        x="Total", y="rotulo", orientation="h",
        text="Total", color="Total",
        color_continuous_scale="Blues", title=titulo,
    )

    fig.update_traces(
        texttemplate="%{x:,}", textposition="outside",
        hovertemplate="<b>%{y}</b><br>AIH: %{x:,}<extra></extra>",
    )

    fig.update_layout(
        **_BASE, **_HOVER,
        height=440,
        yaxis=dict(autorange="reversed", **_GRID),
        xaxis=dict(showticklabels=False, **_GRID),
        coloraxis_showscale=False,
        margin=dict(l=10, r=0, t=35, b=10),
        title_font=dict(size=13),
    )

    return fig, _CONFIG


def create_annual_evolution(df_ser, municipio):
    """Evolução anual — recebe df_ser já filtrado por município e ano."""

    df_an = (
        df_ser
        .assign(ano=df_ser["data"].dt.year)
        .groupby("ano")["quantidade"]
        .sum()
        .reset_index()
    )
    df_an = df_an[df_an["quantidade"] > 0]

    if municipio == "Todos os municípios":
        titulo = "Evolução Anual – SC"
    else:
        titulo = f"Evolução – {municipio}"

    fig = px.line(
        df_an,
        x="ano", y="quantidade",
        markers=True, line_shape="spline",
        title=titulo,
    )

    fig.update_traces(
        line=dict(color="#fbbf24", width=2.5),
        marker=dict(size=8, color="#fbbf24"),
        fill="tozeroy",
        fillcolor="rgba(251,191,36,0.07)",
        hovertemplate="<b>%{x}</b><br>AIH: %{y:,}<extra></extra>",
    )

    fig.update_layout(
        **_BASE, **_HOVER,
        height=440,
        xaxis=dict(dtick=1, **_GRID),
        yaxis=dict(**_GRID),
        margin=dict(l=10, r=10, t=35, b=10),
        title_font=dict(size=13),
    )

    return fig, df_an, _CONFIG


def create_growth_chart(df_ser, periodos_filtro):
    """
    Quais municípios mais cresceram?

    Compara os últimos 12 períodos com os 12 anteriores.
    Isso é mais confiável do que dividir o intervalo ao meio —
    evita o problema de municípios com dados só em parte do histórico.

    Municípios sem dados nos dois blocos são excluídos automaticamente,
    por isso o gráfico pode mostrar menos de 10 barras quando o
    intervalo selecionado é curto ou o dataset tem períodos irregulares.
    """
    import streamlit as st

    # usa os últimos 12 vs 12 anteriores (igual ao metrics.py)
    # se o intervalo filtrado tiver menos de 24 períodos, usa metade de cada lado
    if len(periodos_filtro) >= 24:
        recentes   = periodos_filtro[-12:]
        anteriores = periodos_filtro[-24:-12]
    else:
        meio       = len(periodos_filtro) // 2
        recentes   = periodos_filtro[meio:]
        anteriores = periodos_filtro[:meio]

    if not recentes or not anteriores:
        st.info("Selecione um intervalo maior para ver o crescimento.")
        return px.bar(title="Crescimento (intervalo insuficiente)"), _CONFIG

    soma_rec = (
        df_ser[df_ser["periodo"].isin(recentes)]
        .groupby("municipio")["quantidade"]
        .sum()
    )
    soma_ant = (
        df_ser[df_ser["periodo"].isin(anteriores)]
        .groupby("municipio")["quantidade"]
        .sum()
    )

    df_c = pd.DataFrame({"rec": soma_rec, "ant": soma_ant}).dropna()

    # exige dados nos dois períodos — sem isso a variação não faz sentido
    df_c = df_c[(df_c["ant"] > 0) & (df_c["rec"] > 0)].copy()

    if df_c.empty:
        st.info("Sem municípios com dados suficientes nos dois períodos.")
        return px.bar(title="Crescimento (sem dados)"), _CONFIG

    df_c["variacao_pct"] = (
        (df_c["rec"] - df_c["ant"]) / df_c["ant"] * 100
    ).round(1)

    df_c = (
        df_c
        .sort_values("variacao_pct", ascending=False)
        .head(10)
        .reset_index()
    )

    # avisa quando sobrar menos de 10 municípios válidos
    if len(df_c) < 10:
        st.caption(
            f"⚠️ {len(df_c)} municípios com dados nos dois períodos comparados. "
            "Amplie o intervalo de anos para ver mais resultados."
        )

    cores = ["#3dd68c" if v >= 0 else "#ff6666" for v in df_c["variacao_pct"]]

    fig = px.bar(
        df_c,
        x="variacao_pct", y="municipio", orientation="h",
        text="variacao_pct",
        title="Top 10 – Maior Crescimento (%)",
    )

    fig.update_traces(
        marker_color=cores,
        texttemplate="%{x:.1f}%", textposition="outside",
        hovertemplate="<b>%{y}</b><br>Variação: %{x:.1f}%<extra></extra>",
    )

    fig.update_layout(
        **_BASE, **_HOVER,
        height=440,
        yaxis=dict(autorange="reversed", **_GRID),
        xaxis=dict(ticksuffix="%", **_GRID),
        margin=dict(l=10, r=80, t=35, b=10),
        title_font=dict(size=13),
    )

    return fig, _CONFIG


def create_year_comparison(df_ser, municipio, anos_filtro):
    """
    Comparativo entre anos — barras agrupadas.
    Mostra os 3 anos mais recentes dentro do intervalo selecionado.
    """

    ultimos_3 = sorted(anos_filtro)[-3:]

    df_comp = (
        df_ser[df_ser["data"].dt.year.isin(ultimos_3)]
        .assign(ano=lambda x: x["data"].dt.year.astype(str))
        .groupby(["municipio", "ano"])["quantidade"]
        .sum()
        .reset_index()
    )

    if municipio == "Todos os municípios":
        top10   = df_comp.groupby("municipio")["quantidade"].sum().nlargest(10).index
        df_comp = df_comp[df_comp["municipio"].isin(top10)]
        titulo  = f"Comparativo – Top 10 ({', '.join(map(str, ultimos_3))})"
    else:
        titulo = f"Comparativo Anual – {municipio}"

    if df_comp.empty:
        return px.bar(title="Sem dados para o período selecionado"), _CONFIG

    fig = px.bar(
        df_comp,
        x="municipio", y="quantidade",
        color="ano", barmode="group",
        text="quantidade",
        color_discrete_sequence=["#38bdf8", "#fbbf24", "#c084fc"],
        title=titulo,
    )

    fig.update_traces(
        texttemplate="%{y:,}", textposition="outside",
        hovertemplate="<b>%{x}</b> – %{fullData.name}<br>AIH: %{y:,}<extra></extra>",
    )

    fig.update_layout(
        **_BASE, **_HOVER,
        height=440,
        xaxis=dict(tickangle=-30, **_GRID),
        yaxis=dict(**_GRID),
        legend=dict(title="Ano", font=dict(color="#8ab4cc")),
        margin=dict(l=10, r=10, t=35, b=80),
        title_font=dict(size=13),
    )

    return fig, _CONFIG