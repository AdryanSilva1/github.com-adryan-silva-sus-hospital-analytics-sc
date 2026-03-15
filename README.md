# SUS Hospital Analytics — Santa Catarina
### Dashboard de Internações Hospitalares (AIH · SIH/DATASUS)

Projeto de **análise de dados aplicados à saúde pública**, utilizando dados abertos
do SUS para explorar padrões de internações hospitalares no estado de Santa Catarina.

O dashboard foi desenvolvido para demonstrar técnicas de **data analysis,
visualização e construção de dashboards interativos** com Python.

---

## Tecnologias

- **Python** — linguagem principal
- **Pandas** — limpeza e transformação de dados
- **Streamlit** — framework do dashboard web
- **Plotly** — gráficos interativos

---

## Fonte de Dados

Dados públicos do **SIH/SUS (Sistema de Informações Hospitalares)**
disponibilizados pelo **Ministério da Saúde**, acessados via TabNet.

🔗 https://datasus.saude.gov.br/

Dataset exportado diretamente do TabNet com as seguintes características:

- Abrangência: 138 municípios de Santa Catarina
- Períodos disponíveis: Jun/2015 → Jan/2026
- Períodos analisados: 51 registros mensais disponíveis no export
- Total de internações: 1.767.980 AIH aprovadas

---

## Como Rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sus-hospital-analytics-sc.git

# 2. Entre no diretório
cd sus-hospital-analytics-sc

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o dashboard
python -m streamlit run app.py

# ⚠️ Nunca rode com: python app.py
# O Streamlit precisa do seu próprio servidor para funcionar
```

Acesse em: **http://localhost:8501**

---

## Estrutura do Projeto

```
sus-hospital-analytics-sc/
│
├── app.py                  ← orquestrador principal
├── styles.css              ← estilos visuais (Roboto, degradê, cards)
├── requirements.txt
│
├── data/
│   └── raw/
│       └── dados_sc.csv    ← CSV exportado do TabNet
│
├── src/
│   ├── data_loader.py      ← leitura do CSV bruto
│   ├── data_processing.py  ← limpeza, conversão e transformação wide → long
│   └── metrics.py          ← cálculo de KPIs e variações
│
└── dashboard/
    ├── layout.py           ← cabeçalho, cards, seções e insights
    └── charts.py           ← gráficos Plotly
```

---

## Funcionalidades

- **4 KPIs** — total de AIH, municípios, líder e concentração Top 5
- **Ranking** — top 15 municípios por volume de AIH
- **Evolução anual** — linha histórica com variação percentual automática
- **Crescimento** — top 10 municípios que mais cresceram no período
- **Comparativo anual** — barras agrupadas pelos 3 anos mais recentes
- **Tabela** — dados detalhados com % do estado por município
- **3 filtros** — município, intervalo de anos e AIH mínimas

---

## Limitações Conhecidas

### Gráfico de Crescimento — pode mostrar menos de 10 municípios

O gráfico compara dois blocos de períodos (12 mais recentes vs 12 anteriores).
Um município só aparece se tiver dados nos **dois** blocos.

O TabNet não exporta todos os meses de todos os anos — a maioria dos municípios
só começou a registrar AIH recentemente, o que reduz o número de barras exibidas.

**Como contornar:** selecione um intervalo de anos mais amplo no filtro lateral.
Um aviso automático aparece quando o gráfico tiver menos de 10 municípios válidos.

---

### Variação Semestral (card KPI)

Compara os 6 períodos mais recentes com os 6 anteriores disponíveis no dataset.
Como o TabNet exporta períodos irregulares, os "6 anteriores" podem não
corresponder exatamente a um semestre calendário.

---

## Melhorias Futuras

- [ ] Filtros adicionais (procedimento, faixa etária, sexo)
- [ ] Comparativo entre estados
- [ ] Gráfico de sazonalidade mensal
- [ ] Exportar dados filtrados como CSV
- [ ] Trendline de regressão na evolução anual
- [ ] Deploy no Streamlit Cloud para acesso público

---

## Autor

**Adryan Silva Santos**
Analista de Dados · Automação · Dashboards · Saúde

🔗 [LinkedIn](https://www.linkedin.com/in/adryan-silva-santos)
🔗 [GitHub](https://github.com/seu-usuario)

---

## Desenvolvimento

Backend, pipeline de dados, lógica de negócio e arquitetura do projeto
desenvolvidos por Adryan Silva Santos.
Interface e estilos visuais desenvolvidos com auxílio de IA generativa.