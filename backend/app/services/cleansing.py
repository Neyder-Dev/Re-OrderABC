import pandas as pd
from typing import Tuple

# Palabras clave de productos excluidos de esta bodega
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

def clean_matr780(file_bytes: bytes) -> Tuple[pd.DataFrame, dict]:
    """
    Limpia y normaliza el reporte MATR780 de Protheus.
    Retorna un DataFrame limpio y un reporte de limpieza.
    """
    report = {
        "filas_originales": 0,
        "filas_validas": 0,
        "skus_unicos": 0,
        "duplicados_removidos": 0,
        "filas_sin_cantidad": 0,
        "filas_sin_sku": 0,
        "skus_excluidos": 0,
        "rango_fechas": {}
    }

    # Leer el Excel raw
    df_raw = pd.read_excel(file_bytes, header=None)
    report["filas_originales"] = len(df_raw)

    # Extraer solo filas de detalle:
    # SKU en col 0 (numérico de 8+ dígitos), cantidad en col 6
    records = []
    for _, row in df_raw.iterrows():
        sku = str(row[0]).strip() if pd.notna(row[0]) else ""
        if sku.isdigit() and len(sku) >= 8:
            records.append({
                "sku":         sku,
                "descripcion": str(row[1]).strip() if pd.notna(row[1]) else "",
                "num_doc":     str(row[2]).strip() if pd.notna(row[2]) else "",
                "fecha":       row[4] if pd.notna(row[4]) else None,
                "unidad":      str(row[5]).strip() if pd.notna(row[5]) else "",
                "cantidad":    row[6] if pd.notna(row[6]) else None,
                "valor_unit":  row[7] if pd.notna(row[7]) else 0,
                "valor_total": row[8] if pd.notna(row[8]) else 0,
            })

    if not records:
        raise ValueError(
            "No se encontraron filas válidas en el archivo. "
            "Verifica que sea un reporte MATR780 exportado como Planilla y que la columna A contenga SKUs numéricos de 8 o más dígitos."
        )

    df = pd.DataFrame(records)

    # Excluir productos no almacenados en bodega
    mask_excluidos = df['descripcion'].apply(producto_excluido)
    excluidos_count = mask_excluidos.sum()
    report["skus_excluidos"] = int(excluidos_count)
    df = df[~mask_excluidos]
    
    if df.empty:
        raise ValueError(
            "El archivo no contiene datos válidos. "
            "Verifica que sea un reporte MATR780 exportado como Planilla."
        )

    # Filas sin cantidad
    sin_cantidad = df["cantidad"].isna().sum()
    report["filas_sin_cantidad"] = int(sin_cantidad)
    df = df.dropna(subset=["cantidad"])

    # Convertir tipos
    df["cantidad"]    = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
    df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce").fillna(0)
    df["valor_unit"]  = pd.to_numeric(df["valor_unit"], errors="coerce").fillna(0)

    # Eliminar filas con cantidad 0 o negativa
    df = df[df["cantidad"] > 0]

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