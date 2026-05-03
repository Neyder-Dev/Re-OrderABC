import pandas as pd
from typing import Tuple


def run_abc(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Corre el algoritmo ABC sobre el DataFrame limpio del MATR780.
    Clasifica cada SKU en zona A, B o C según valor total vendido.
    Retorna DataFrame con clasificación y resumen estadístico.
    """

    # Agrupar por SKU — sumar todo el período
    abc = df.groupby("sku").agg(
        descripcion=("descripcion", "first"),
        unidad=("unidad", "first"),
        cantidad_total=("cantidad", "sum"),
        valor_total=("valor_total", "sum"),
        num_transacciones=("num_doc", "nunique"),
    ).reset_index()

    # Ordenar de mayor a menor valor
    abc = abc.sort_values("valor_total", ascending=False).reset_index(drop=True)

    # Calcular porcentaje acumulado
    total_valor = abc["valor_total"].sum()
    abc["pct_valor"]      = abc["valor_total"] / total_valor * 100
    abc["pct_acumulado"]  = abc["pct_valor"].cumsum()

    # Clasificar zonas
    # A → acumulado ≤ 80%
    # B → acumulado ≤ 95%
    # C → resto
    def clasificar(pct):
        if pct <= 80:
            return "A"
        elif pct <= 95:
            return "B"
        else:
            return "C"

    abc["zona_abc"] = abc["pct_acumulado"].apply(clasificar)

    # Resumen
    resumen = abc.groupby("zona_abc").agg(
        skus=("sku", "count"),
        valor=("valor_total", "sum"),
    ).reset_index()
    resumen["pct_skus"]  = (resumen["skus"] / len(abc) * 100).round(2)
    resumen["pct_valor"] = (resumen["valor"] / total_valor * 100).round(2)

    summary = {
        "total_skus":   len(abc),
        "total_valor":  float(total_valor),
        "zonas": resumen.to_dict(orient="records"),
    }

    return abc, summary