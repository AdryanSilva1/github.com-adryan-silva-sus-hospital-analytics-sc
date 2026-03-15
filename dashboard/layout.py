import streamlit as st


def render_header(data_inicio, data_fim, total_municipios):
    """Cabeçalho profissional com badges de contexto."""
    st.markdown(f"""
        <div class="header-wrap">
            <div class="header-icon"><img src="https://img.odcdn.com.br/wp-content/uploads/2020/07/20200703014442.jpg" height="80px"></div>
            <div>
                <p class="header-titulo">Dashboard SUS — Santa Catarina</p>
                <p class="header-subtitulo">
                    Autorização de Internação Hospitalar (AIH) · SIH/DATASUS · Ministério da Saúde
                </p>
                <div>
                    <span class="header-badge">📅 {data_inicio} → {data_fim}</span>
                    <span class="header-badge">📍 {total_municipios} municípios</span>
                    <span class="header-badge">🇧🇷 Santa Catarina</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_section(titulo):
    st.markdown(f'<p class="secao">{titulo}</p>', unsafe_allow_html=True)


def render_insight(texto):
    st.markdown(f'<div class="insight">📌 {texto}</div>', unsafe_allow_html=True)


def render_card(col, icone, rotulo, valor, delta, cor):
    col.markdown(f"""
        <div class="card" style="--accent:{cor}">
            <div class="card-icon">{icone}</div>
            <div class="card-label">{rotulo}</div>
            <div class="card-valor">{valor}</div>
            <div class="card-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)  