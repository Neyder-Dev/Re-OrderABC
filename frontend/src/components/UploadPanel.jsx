import { useState, useRef } from 'react'
import { uploadMatr780 } from '../services/api'

function UploadPanel({ onUploadSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filename, setFilename] = useState(null)
  const inputRef = useRef()

  const handleFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setFilename(file.name)
    setError(null)
    setLoading(true)
    try {
      const { data } = await uploadMatr780(file)
      onUploadSuccess(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el archivo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-700 mb-4">
        Cargar reporte MATR780
      </h2>

      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition"
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls"
          className="hidden"
          onChange={handleFile}
        />

        {loading ? (
          <div className="text-blue-500 font-medium animate-pulse">
            Procesando algoritmo ABC...
          </div>
        ) : filename ? (
          <div className="text-green-600 font-medium">✅ {filename}</div>
        ) : (
          <div>
            <p className="text-gray-400 text-sm">
              Haz click o arrastra el archivo MATR780 aquí
            </p>
            <p className="text-gray-300 text-xs mt-1">.xlsx o .xls</p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-red-500 text-sm mt-3">❌ {error}</p>
      )}
    </div>
  )
}

export default UploadPanel