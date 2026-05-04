import { useState, useRef } from 'react'
import { uploadMatr780, uploadMatr425 } from '../services/api'

function UploadPanel({ titulo, descripcion, onUploadSuccess, tipo }) {
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [filename, setFilename] = useState(null)
  const inputRef                = useRef()

  const handleFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setFilename(file.name)
    setError(null)
    setLoading(true)
    try {
      const fn = tipo === 'matr780' ? uploadMatr780 : uploadMatr425
      const { data } = await fn(file)
      onUploadSuccess(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el archivo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-5">
      <h2 className="text-sm font-semibold text-gray-700 mb-1">{titulo}</h2>
      <p className="text-xs text-gray-400 mb-3">{descripcion}</p>

      <div
        className="border-2 border-dashed border-gray-200 rounded-lg p-5 text-center cursor-pointer hover:border-blue-400 transition"
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
          <div className="text-blue-500 text-sm font-medium animate-pulse">
            Procesando...
          </div>
        ) : filename ? (
          <div className="text-green-600 text-sm font-medium">✅ {filename}</div>
        ) : (
          <div>
            <p className="text-gray-400 text-xs">Haz click o arrastra el archivo aquí</p>
            <p className="text-gray-300 text-xs mt-1">.xlsx o .xls</p>
          </div>
        )}
      </div>

      {error && <p className="text-red-500 text-xs mt-2">❌ {error}</p>}
    </div>
  )
}

export default UploadPanel