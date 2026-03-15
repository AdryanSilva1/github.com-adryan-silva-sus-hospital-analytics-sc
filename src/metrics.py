def calculate_top5_share(df):
    """Percentual das AIH concentradas nos 5 maiores municípios."""
    total = df["Total"].sum()
    top5  = df.head(5)["Total"].sum()
    return round(top5 / total * 100, 1)


def semester_variation(df_long, periodos):
    """
    Variação percentual entre os últimos 6 meses e os 6 anteriores.
    Retorna um número positivo (crescimento) ou negativo (queda).
    """
    
    # Compara dois semestres (6 meses cada)
    # Nota: períodos irregulares do TabNet podem excluir alguns meses

    ultimos_6 = periodos[-6:]
    ant_6     = periodos[-12:-6]

    soma_rec = df_long[df_long["periodo"].isin(ultimos_6)]["quantidade"].sum()
    soma_ant = df_long[df_long["periodo"].isin(ant_6)]["quantidade"].sum()

    if soma_ant == 0:
        return 0

    return round((soma_rec - soma_ant) / soma_ant * 100, 1)