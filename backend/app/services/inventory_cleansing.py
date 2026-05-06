import pandas as pd
from typing import Tuple

# Palabras clave de productos que NO se almacenan en esta bodega
PRODUCTOS_EXCLUIDOS = [
    'OPTISLIP',
    'INCROMOLD',
    'INCROSLIP',
    'KEMELIX',
    'ATMER',
]


def producto_excluido(descripcion: str) -> bool:
    desc_upper = str(descripcion).upper()
    return any(keyword in desc_upper for keyword in PRODUCTOS_EXCLUIDOS)


def clean_matr425(file_bytes) -> Tuple[pd.DataFrame, dict]:
    """
    Limpia y normaliza el reporte MATR425 de Protheus.
    Solo considera el depósito 02 (VENTA) con saldo > 0.
    Excluye productos que no se almacenan en esta bodega.
    Agrupa por SKU sumando todos los lotes.
    """
    report = {
        "filas_originales": 0,
        "skus_en_bodega": 0,
        "skus_excluidos": 0,
        "productos_excluidos": [],
        "depositos_ignorados": [],
    }

    df = pd.read_excel(file_bytes, header=1)
    report["filas_originales"] = len(df)

    # Depositos ignorados
    otros = df[df['Deposito'] != 2]['Deposito'].unique().tolist()
    report["depositos_ignorados"] = [int(d) for d in otros]

    # Filtrar solo deposito 02 con saldo positivo
    df_venta = df[(df['Deposito'] == 2) & (df['Saldo 1a.U.M.'] > 0)].copy()

    # Convertir SKU a string
    df_venta['Producto'] = df_venta['Producto'].astype(str).str.zfill(8)

    # Identificar y excluir productos no almacenados en bodega
    mask_excluidos = df_venta['Descripcion'].apply(producto_excluido)
    excluidos = df_venta[mask_excluidos]['Descripcion'].unique().tolist()
    report["productos_excluidos"] = excluidos
    report["skus_excluidos"] = len(
        df_venta[mask_excluidos]['Producto'].unique()
    )

    df_venta = df_venta[~mask_excluidos]

    # Agrupar por SKU
    inventario = df_venta.groupby('Producto').agg(
        descripcion=('Descripcion', 'first'),
        saldo_total=('Saldo 1a.U.M.', 'sum'),
        num_lotes=('Lote', 'nunique'),
    ).reset_index()

    inventario = inventario.rename(columns={'Producto': 'sku'})
    inventario = inventario.sort_values('saldo_total', ascending=False)

    report["skus_en_bodega"] = len(inventario)

    return inventario, report