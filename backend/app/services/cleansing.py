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


def clean_matr780(file_bytes: bytes) -> Tuple[pd.DataFrame, dict]:
    """
    Limpia el reporte MATR780 de Protheus.
    Estructura esperada (índices base 0):
      Col 0: Cliente
      Col 1: Tienda
      Col 2: Nombre
      Col 3: Observacion
      Col 4: Producto (SKU numérico 8+ dígitos)
      Col 5: Descripcion
      Col 6: Num. de Doc.
      Col 7: Serie
      Col 8: Emision (fecha)
      Col 9: Unidad
      Col 10: Cantidad
      Col 11: Valor Unit.
      Col 12: Valor Total
      Col 13: Vendedor
    """
    report = {
        "filas_originales": 0,
        "filas_validas": 0,
        "skus_unicos": 0,
        "filas_sin_cantidad": 0,
        "filas_sin_sku": 0,
        "skus_excluidos": 0,
        "rango_fechas": {}
    }

    df_raw = pd.read_excel(file_bytes, header=None)
    report["filas_originales"] = len(df_raw)

    records = []
    for _, row in df_raw.iterrows():
        try:
            sku = str(int(float(row[4]))).strip() if pd.notna(row[4]) else ""
        except (ValueError, TypeError):
            sku = str(row[4]).strip() if pd.notna(row[4]) else ""

        if sku.isdigit() and len(sku) >= 8:
            records.append({
                "sku":         sku,
                "descripcion": str(row[5]).strip() if pd.notna(row[5]) else "",
                "num_doc":     str(row[6]).strip() if pd.notna(row[6]) else "",
                "fecha":       row[8] if pd.notna(row[8]) else None,
                "unidad":      str(row[9]).strip() if pd.notna(row[9]) else "",
                "cantidad":    _parse_numero(row[10]),
                "valor_unit":  _parse_numero(row[11]),
                "valor_total": _parse_numero(row[12]),
            })

    if not records:
        raise ValueError(
            "No se encontraron filas válidas. "
            "Verifica que el archivo sea un MATR780 exportado como Planilla "
            "y que la columna 'Producto' contenga SKUs numéricos de 8 o más dígitos."
        )

    df = pd.DataFrame(records)

    # Excluir productos externos
    mask_excluidos = df['descripcion'].apply(producto_excluido)
    report["skus_excluidos"] = int(mask_excluidos.sum())
    df = df[~mask_excluidos]

    if df.empty:
        raise ValueError(
            "Todos los productos fueron excluidos del análisis. "
            "Verifica la lista de exclusiones o el contenido del archivo."
        )

    # Filas sin cantidad
    sin_cantidad = (df["cantidad"] <= 0).sum()
    report["filas_sin_cantidad"] = int(sin_cantidad)
    df = df[df["cantidad"] > 0]

    if df.empty:
        raise ValueError("No hay productos con cantidad mayor a cero en el archivo.")

    # Rango de fechas
    fechas_validas = df["fecha"].dropna()
    if not fechas_validas.empty:
        report["rango_fechas"] = {
            "inicio": str(fechas_validas.min()),
            "fin":    str(fechas_validas.max())
        }

    report["filas_validas"] = len(df)
    report["skus_unicos"]   = df["sku"].nunique()

    return df, report
