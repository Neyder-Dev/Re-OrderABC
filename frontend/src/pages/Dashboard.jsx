import { useState } from 'react'
import UploadPanel from '../components/UploadPanel'
import StatsBar from '../components/StatsBar'
import RackMap from '../components/RackMap'

function Dashboard() {
  const [uploadResult, setUploadResult] = useState(null)
  const [productos, setProductos] = useState([])

  const handleUploadSuccess = (data) => {
    setUploadResult(data)
    // Simulamos productos con zona ABC para el mapa
    // En la siguiente iteración esto vendrá del endpoint GET /products
    setProductos([])
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
            ✅ {uploadResult.filename} procesado
          </span>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Panel de carga */}
        <UploadPanel onUploadSuccess={handleUploadSuccess} />

        {/* Stats después de cargar */}
        {uploadResult && (
          <>
            <StatsBar stats={uploadResult} />

            {/* Info del reporte */}
            <div className="bg-white rounded-xl shadow p-4 mb-6 text-sm text-gray-500">
              <span className="font-medium text-gray-700">Período analizado: </span>
              {uploadResult.cleansing_report?.rango_fechas?.inicio?.slice(0, 10)} →{' '}
              {uploadResult.cleansing_report?.rango_fechas?.fin?.slice(0, 10)}
              <span className="ml-6 font-medium text-gray-700">Total SKUs: </span>
              {uploadResult.total_skus}
            </div>

            {/* Mapa de racks */}
            <RackMap productos={productos} />
          </>
        )}

        {!uploadResult && (
          <div className="text-center py-20 text-gray-300">
            <p className="text-5xl mb-4">🏭</p>
            <p className="text-lg">Carga un reporte MATR780 para comenzar</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard