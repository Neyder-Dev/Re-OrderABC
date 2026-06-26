import pandas as pd
from typing import Tuple

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


def _parse_saldo(valor) -> float:
    """Convierte saldo que puede venir como string español ' 23.484,00 ' o como float."""
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def clean_matr425(file_bytes) -> Tuple[pd.DataFrame, dict]:
    """
    Limpia el reporte MATR425 de Protheus.
    Estructura esperada (índices base 0):
      Col 0: Producto (SKU)
      Col 1: Descripcion
      Col 2: Sublote
      Col 3: Lote
      Col 4: Deposito
      Col 5: Saldo 1a.U.M.
      Col 6: Reserva 1a.U.M.
      Col 7: Fecha
      Col 8: Fch Validez
      Col 9: Descripcion (tipo depósito)
    Solo considera depósito 02 (VENTA) con saldo > 0.
    """
    report = {
        "filas_originales": 0,
        "skus_en_bodega": 0,
        "skus_excluidos": 0,
        "productos_excluidos": [],
        "depositos_ignorados": [],
    }

    # header=0: la primera fila del Excel es el encabezado
    df = pd.read_excel(file_bytes, header=0)
    report["filas_originales"] = len(df)

    # Normalizar nombre de columnas (quitar espacios)
    df.columns = [str(c).strip() for c in df.columns]

    # Convertir Deposito a string normalizado (sin ceros a la izquierda → "2")
    df['Deposito'] = df['Deposito'].apply(
        lambda x: str(int(float(x))).strip() if pd.notna(x) else ""
    )

    # Parsear Saldo (puede ser string formato español)
    df['Saldo 1a.U.M.'] = df['Saldo 1a.U.M.'].apply(_parse_saldo)

    # Depositos ignorados
    otros = df[df['Deposito'] != '2']['Deposito'].unique().tolist()
    report["depositos_ignorados"] = otros

    # Filtrar solo depósito 02 con saldo positivo
    df_venta = df[(df['Deposito'] == '2') & (df['Saldo 1a.U.M.'] > 0)].copy()

    if df_venta.empty:
        raise ValueError(
            "No se encontraron productos con saldo en el depósito 02. "
            "Verifica que el archivo sea un MATR425 y que existan saldos en depósito 02."
        )

    # Convertir SKU a string con ceros a la izquierda (8 dígitos)
    df_venta['Producto'] = df_venta['Producto'].apply(
        lambda x: str(int(float(x))).zfill(8) if pd.notna(x) else ""
    )

    # Excluir productos externos
    mask_excluidos = df_venta['Descripcion'].apply(producto_excluido)
    excluidos = df_venta[mask_excluidos]['Descripcion'].unique().tolist()
    report["productos_excluidos"] = excluidos
    report["skus_excluidos"] = int(df_venta[mask_excluidos]['Producto'].nunique())
    df_venta = df_venta[~mask_excluidos]

    # Agrupar por SKU sumando todos los lotes
    inventario = df_venta.groupby('Producto').agg(
        descripcion=('Descripcion', 'first'),
        saldo_total=('Saldo 1a.U.M.', 'sum'),
        num_lotes=('Lote', 'nunique'),
    ).reset_index()

    inventario = inventario.rename(columns={'Producto': 'sku'})
    inventario = inventario.sort_values('saldo_total', ascending=False)

    report["skus_en_bodega"] = len(inventario)

    return inventario, report
