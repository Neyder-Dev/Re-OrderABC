import { useState, useEffect } from 'react'
import UploadPanel from '../components/UploadPanel'
import StatsBar from '../components/StatsBar'
import RackMap from '../components/RackMap'
import { getMapa } from '../services/api'

function Dashboard() {
  const [uploadResult, setUploadResult]   = useState(null)
  const [productos, setProductos]         = useState([])
  const [loadingMapa, setLoadingMapa]     = useState(true)

  // Al cargar la página recuperar el mapa desde la DB
  useEffect(() => {
    getMapa()
      .then(({ data }) => {
        setProductos(data.productos)
        if (data.asignados > 0) {
          setUploadResult({
            filename: 'Último cálculo guardado',
            total_skus: data.total_productos,
            skus_zone_a: data.productos.filter(p => p.abc_zone === 'A').length,
            skus_zone_b: data.productos.filter(p => p.abc_zone === 'B').length,
            skus_zone_c: data.productos.filter(p => p.abc_zone === 'C').length,
            cleansing_report: null,
          })
        }
      })
      .catch(() => {})
      .finally(() => setLoadingMapa(false))
  }, [])

  const handleUploadSuccess = (data) => {
    setUploadResult(data)
    // Recargar el mapa después de subir el MATR780
    getMapa().then(({ data: mapa }) => setProductos(mapa.productos))
  }

  const handleStockSuccess = () => {
    // Recargar el mapa después de subir el MATR425
    getMapa().then(({ data: mapa }) => {
      setProductos(mapa.productos)
      setUploadResult(prev => ({
        ...prev,
        filename: 'Inventario actualizado',
        total_skus: mapa.total_productos,
        skus_zone_a: mapa.productos.filter(p => p.abc_zone === 'A').length,
        skus_zone_b: mapa.productos.filter(p => p.abc_zone === 'B').length,
        skus_zone_c: mapa.productos.filter(p => p.abc_zone === 'C').length,
      }))
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">ReOrdena-ABC</h1>
          <p className="text-xs text-gray-400">Optimización logística de bodega</p>
        </div>
        {uploadResult && (
          <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
            ✅ {uploadResult.filename}
          </span>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">

        {/* Paneles de carga */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <UploadPanel
            titulo="1. Cargar ventas (MATR780)"
            descripcion="Clasifica los SKUs en zonas ABC"
            onUploadSuccess={handleUploadSuccess}
            tipo="matr780"
          />
          <UploadPanel
            titulo="2. Cargar inventario (MATR425)"
            descripcion="Asigna posiciones solo a productos con stock"
            onUploadSuccess={handleStockSuccess}
            tipo="matr425"
          />
        </div>

        {/* Loading inicial */}
        {loadingMapa && (
          <div className="text-center py-10 text-gray-400 animate-pulse">
            Cargando mapa de bodega...
          </div>
        )}

        {/* Stats y mapa */}
        {!loadingMapa && uploadResult && (
          <>
            <StatsBar stats={uploadResult} />

            {uploadResult.cleansing_report && (
              <div className="bg-white rounded-xl shadow p-4 mb-6 text-sm text-gray-500">
                <span className="font-medium text-gray-700">Período analizado: </span>
                {uploadResult.cleansing_report?.rango_fechas?.inicio?.slice(0, 10)} →{' '}
                {uploadResult.cleansing_report?.rango_fechas?.fin?.slice(0, 10)}
                <span className="ml-6 font-medium text-gray-700">Total SKUs: </span>
                {uploadResult.total_skus}
              </div>
            )}

            <RackMap productos={productos} />
          </>
        )}

        {!loadingMapa && !uploadResult && (
          <div className="text-center py-20 text-gray-300">
            <p className="text-5xl mb-4">🏭</p>
            <p className="text-lg">Carga el MATR780 y luego el MATR425 para comenzar</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard