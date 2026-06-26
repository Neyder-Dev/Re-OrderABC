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


def _parse_numero(valor) -> float:
    """Convierte valores que pueden venir como string con formato español."""
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
    Limpia el reporte MATR425 de Protheus. Lee por índice de columna.
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

    # Leer sin encabezado para acceder por índice de columna
    df_raw = pd.read_excel(file_bytes, header=None)
    report["filas_originales"] = len(df_raw)

    records = []
    for _, row in df_raw.iterrows():
        # Parsear SKU (col 0) — puede venir como float
        try:
            sku = str(int(float(row[0]))).strip() if pd.notna(row[0]) else ""
        except (ValueError, TypeError):
            sku = str(row[0]).strip() if pd.notna(row[0]) else ""

        if not (sku.isdigit() and len(sku) >= 8):
            continue

        # Parsear depósito (col 4) — normalizar a string sin ceros
        try:
            deposito = str(int(float(row[4]))).strip() if pd.notna(row[4]) else ""
        except (ValueError, TypeError):
            deposito = str(row[4]).strip() if pd.notna(row[4]) else ""

        # Solo depósito 02
        if deposito != '2':
            continue

        saldo = _parse_numero(row[5]) if len(row) > 5 else 0.0
        if saldo <= 0:
            continue

        descripcion = str(row[1]).strip() if pd.notna(row[1]) else ""
        lote        = str(row[3]).strip() if pd.notna(row[3]) else ""

        records.append({
            "sku":        sku,
            "descripcion": descripcion,
            "lote":        lote,
            "deposito":    deposito,
            "saldo":       saldo,
        })

    if not records:
        raise ValueError(
            "No se encontraron productos con saldo en el depósito 02. "
            "Verifica que el archivo sea un MATR425 y que existan registros en depósito 02."
        )

    df = pd.DataFrame(records)

    # Excluir productos externos
    mask_excluidos = df['descripcion'].apply(producto_excluido)
    report["productos_excluidos"] = df[mask_excluidos]['descripcion'].unique().tolist()
    report["skus_excluidos"]      = int(df[mask_excluidos]['sku'].nunique())
    df = df[~mask_excluidos]

    # Agrupar por SKU sumando todos los lotes
    inventario = df.groupby('sku').agg(
        descripcion=('descripcion', 'first'),
        saldo_total=('saldo', 'sum'),
        num_lotes=('lote', 'nunique'),
    ).reset_index()

    inventario = inventario.sort_values('saldo_total', ascending=False)
    report["skus_en_bodega"] = len(inventario)

    return inventario, report
