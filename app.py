# =============================================================
# app.py — Dashboard SUS – Santa Catarina
#
# Como rodar:
#   pip install -r requirements.txt
#   python -m streamlit run app.py
# =============================================================

import streamlit as st

from src.data_loader      import load_raw_data
from src.data_processing  import clean_dataset, convert_numeric, reshape_long, sort_periods
from src.metrics          import calculate_top5_share, semester_variation
from dashboard.layout     import render_header, render_section, render_insight, render_card
from dashboard.charts     import (create_ranking, create_annual_evolution,
                                   create_growth_chart, create_year_comparison)


# ── Configuração ─────────────────────────────────────────────
st.set_page_config(page_title="Dashboard SUS – SC", page_icon="🏥", layout="wide")

with open("styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── Dados ────────────────────────────────────────────────────
df_raw           = load_raw_data()
df               = clean_dataset(df_raw)
df, cols_periodo = convert_numeric(df)
df_long          = reshape_long(df, cols_periodo)
periodos         = sort_periods(cols_periodo)
anos             = sorted(df_long["data"].dt.year.unique())


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filtros")
    st.markdown("---")

    municipio = st.selectbox(
        "🔍 Município",
        ["Todos os municípios"] + df["municipio"].tolist(),
    )

    ano_min, ano_max = int(min(anos)), int(max(anos))
    ano_ini, ano_fim = st.select_slider(
        "📅 Intervalo de anos",
        options=list(range(ano_min, ano_max + 1)),
        value=(ano_min, ano_max),
    )

    max_aih = int(df["Total"].max())
    min_aih = st.slider("📊 AIH mínimas", 0, max_aih // 2, 0, step=500)

    st.markdown("---")
    st.markdown("### 🏆 Top 3")
    for i, (_, row) in enumerate(df.head(3).iterrows()):
        st.markdown(f"""
            <div class="top3-box">
                <div class="top3-medal">{"🥇🥈🥉"[i*2:i*2+2]}</div>
                <div>
                    <div class="top3-nome">{row['municipio']}</div>
                    <div class="top3-val">{int(row['Total']):,} AIH</div>
                </div>
            </div>""", unsafe_allow_html=True)


# ── Filtragem ────────────────────────────────────────────────
if municipio == "Todos os municípios":
    df_vis = df[df["Total"] >= min_aih].copy()
    df_ser = df_long[df_long["municipio"].isin(df_vis["municipio"])].copy()
else:
    df_vis = df[df["municipio"] == municipio].copy()
    df_ser = df_long[df_long["municipio"] == municipio].copy()

df_ser = df_ser[
    (df_ser["data"].dt.year >= ano_ini) &
    (df_ser["data"].dt.year <= ano_fim)
].copy()

periodos_filtro = [p for p in periodos if ano_ini <= int(p.split("/")[0]) <= ano_fim]
anos_filtro     = [a for a in anos if ano_ini <= a <= ano_fim]


# ── Métricas ─────────────────────────────────────────────────
total     = int(df_vis["Total"].sum())
n_mun     = df_vis["municipio"].nunique()
lider     = df_vis.iloc[0] if not df_vis.empty else None
top5      = calculate_top5_share(df)
var_sem   = semester_variation(df_ser, periodos_filtro)
delta_cls = "delta-up" if var_sem >= 0 else "delta-down"
delta_txt = (
    f'<span class="{delta_cls}">{"↑" if var_sem >= 0 else "↓"} '
    f'{abs(var_sem):.1f}% vs sem. ant.</span>'
)


# ── Cabeçalho ────────────────────────────────────────────────
render_header(
    data_inicio=df_long["data"].min().strftime("%b/%Y"),
    data_fim=df_long["data"].max().strftime("%b/%Y"),
    total_municipios=df["municipio"].nunique(),
)
st.markdown("<br>", unsafe_allow_html=True)


# ── Seção 1: KPIs ────────────────────────────────────────────
render_section("Indicadores")
c1, c2, c3, c4 = st.columns(4)

render_card(c1, "🏥", "AIH Aprovadas",
            f"{total:,}", delta_txt, "#38bdf8")

render_card(c2, "📍", "Municípios com Dados",
            f"{n_mun}",
            f'<span class="delta-neu">{ano_ini} → {ano_fim}</span>',
            "#60a5fa")

render_card(c3, "🥇", f"Líder · {lider['municipio'] if lider is not None else '–'}",
            f"{int(lider['Total']):,}" if lider is not None else "–",
            f'<span class="delta-neu">'
            f'{round(lider["Total"] / df["Total"].sum() * 100, 1) if lider is not None else 0}'
            f'% do estado</span>',
            "#fbbf24")

render_card(c4, "🏙️", "Concentração Top 5",
            f"{top5}%",
            '<span class="delta-neu">dos 5 maiores municípios</span>',
            "#c084fc")

st.markdown("<br>", unsafe_allow_html=True)


# ── Seção 2: Ranking + Evolução anual ────────────────────────
render_section("Ranking e Evolução Anual")
col_r, col_e = st.columns(2)

with col_r:
    fig, cfg = create_ranking(df_vis, municipio)
    st.plotly_chart(fig, width="stretch", config=cfg)
    if municipio == "Todos os municípios" and not df_vis.empty:
        pct1 = round(df_vis.iloc[0]["Total"] / df["Total"].sum() * 100, 1)
        render_insight(
            f"<span>{df_vis.iloc[0]['municipio']}</span> concentra <span>{pct1}%</span>. "
            f"Top 5 juntos: <span>{top5}%</span> do estado."
        )

with col_e:
    fig, df_an, cfg = create_annual_evolution(df_ser, municipio)
    st.plotly_chart(fig, width="stretch", config=cfg)
    if len(df_an) >= 2:
        a1  = df_an.iloc[-2]["quantidade"]
        a2  = df_an.iloc[-1]["quantidade"]
        var = (a2 - a1) / a1 * 100
        cls = "delta-up" if var > 0 else "delta-down"
        render_insight(
            f"<span>{int(df_an.iloc[-1]['ano'])}</span>: "
            f'<span class="{cls}">{"↑" if var > 0 else "↓"} {abs(var):.1f}%</span> '
            f"vs {int(df_an.iloc[-2]['ano'])} "
            f"({int(a1):,} → <span>{int(a2):,}</span> AIH)."
        )


# ── Seção 3: Crescimento + Comparativo ───────────────────────
render_section("Crescimento e Comparativo por Ano")
col_g, col_c = st.columns(2)

with col_g:
    fig, cfg = create_growth_chart(df_ser, periodos_filtro)
    st.plotly_chart(fig, width="stretch", config=cfg)

with col_c:
    fig, cfg = create_year_comparison(df_ser, municipio, anos_filtro)
    st.plotly_chart(fig, width="stretch", config=cfg)


# ── Seção 4: Tabela ──────────────────────────────────────────
render_section("Tabela de Dados")

ultimos_6 = periodos_filtro[-6:] if len(periodos_filtro) >= 6 else periodos_filtro
cols_tab  = ["municipio"] + [c for c in ultimos_6 if c in df_vis.columns] + ["Total"]

df_tab = df_vis[cols_tab].copy()
df_tab["% do Estado"] = (df_tab["Total"] / df["Total"].sum() * 100).round(2)
df_tab = (
    df_tab
    .rename(columns={"municipio": "Município", "Total": "Total AIH"})
    .sort_values("Total AIH", ascending=False)
)

st.dataframe(
    df_tab, width="stretch", hide_index=True, height=320,
    column_config={
        "Total AIH":   st.column_config.NumberColumn(format="%d"),
        "% do Estado": st.column_config.NumberColumn(format="%.2f%%"),
        **{p: st.column_config.NumberColumn(format="%d") for p in ultimos_6},
    },
)


# ── Rodapé ───────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center;color:#2a4060;font-size:.75rem;font-family:Roboto,sans-serif">'
    'Fonte: Ministério da Saúde · SIH/SUS · TabNet · Python · Streamlit · Plotly'
    '</p>',
    unsafe_allow_html=True,
)