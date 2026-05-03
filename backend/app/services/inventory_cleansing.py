import pandas as pd
from typing import Tuple


def clean_matr425(file_bytes) -> Tuple[pd.DataFrame, dict]:
    """
    Limpia y normaliza el reporte MATR425 de Protheus.
    Solo considera el depósito 02 (VENTA) con saldo > 0.
    Agrupa por SKU sumando todos los lotes.
    """
    report = {
        "filas_originales": 0,
        "skus_en_bodega": 0,
        "skus_sin_stock": 0,
        "depositos_ignorados": []
    }

    df = pd.read_excel(file_bytes, header=1)
    report["filas_originales"] = len(df)

    # Depositos ignorados
    otros = df[df['Deposito'] != 2]['Deposito'].unique().tolist()
    report["depositos_ignorados"] = [int(d) for d in otros]

    # Filtrar solo deposito 02 con saldo positivo
    df_venta = df[(df['Deposito'] == 2) & (df['Saldo 1a.U.M.'] > 0)].copy()

    # Convertir SKU a string con ceros a la izquierda
    df_venta['Producto'] = df_venta['Producto'].astype(str).str.zfill(8)

    # Agrupar por SKU
    inventario = df_venta.groupby('Producto').agg(
        descripcion=('Descripcion', 'first'),
        saldo_total=('Saldo 1a.U.M.', 'sum'),
        num_lotes=('Lote', 'nunique')
    ).reset_index()

    inventario = inventario.rename(columns={'Producto': 'sku'})
    inventario = inventario.sort_values('saldo_total', ascending=False)

    report["skus_en_bodega"] = len(inventario)

    return inventario, report