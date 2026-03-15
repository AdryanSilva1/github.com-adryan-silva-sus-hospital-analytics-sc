import pandas as pd

# Tabela de conversão: abreviação do mês → número
MESES = {
    "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
    "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
}


def clean_dataset(df):
    """
    Remove o rodapé do TabNet e separa o código IBGE do nome do município.
    Exemplo: "420010 ABELARDO LUZ" → codigo_ibge="420010", municipio="Abelardo Luz"
    """
    # Mantém só linhas que começam com 6 dígitos (código IBGE)
    df = df[df["Município"].str.match(r"^\d{6}", na=False)].copy()

    df["codigo_ibge"] = df["Município"].str[:6]
    df["municipio"]   = df["Município"].str[7:].str.strip().str.title()

    return df


def convert_numeric(df):
    """
    Converte colunas de período e Total para inteiro.
    O TabNet usa "-" para valores vazios, que viramos 0.
    """
    # Colunas de período = tudo que não for controle
    cols_ctrl    = {"Município", "Total", "codigo_ibge", "municipio"}
    cols_periodo = [c for c in df.columns if c not in cols_ctrl]

    for col in cols_periodo + ["Total"]:
        df[col] = pd.to_numeric(df[col].replace("-", 0), errors="coerce").fillna(0).astype(int)

    # Ordena do município com mais AIH para o com menos
    df = df.sort_values("Total", ascending=False).reset_index(drop=True)

    return df, cols_periodo


def reshape_long(df, cols_periodo):
    """
    Transforma o DataFrame de formato wide (uma coluna por mês)
    para formato long (uma linha por município/mês).
    """
    df_long = df.melt(
        id_vars=["codigo_ibge", "municipio"],
        value_vars=cols_periodo,
        var_name="periodo",
        value_name="quantidade",
    )

    # Converte "2024/Jan" em uma data real para ordenação correta
    df_long["data"] = df_long["periodo"].apply(
        lambda p: pd.Timestamp(int(p.split("/")[0]), MESES[p.split("/")[1]], 1)
    )

    df_long = df_long.sort_values(["municipio", "data"]).reset_index(drop=True)
    return df_long


def sort_periods(cols_periodo):
    """Retorna os períodos em ordem cronológica."""
    return sorted(cols_periodo, key=lambda p: (int(p.split("/")[0]), MESES[p.split("/")[1]]))