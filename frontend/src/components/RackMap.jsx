import { useState } from 'react'
import api from '../services/api'

const ZONE_COLORS = {
  A: 'bg-red-500 text-white border-red-600',
  B: 'bg-yellow-400 text-gray-800 border-yellow-500',
  C: 'bg-green-500 text-white border-green-600',
}

const ZONE_COLORS_EMPTY = {
  A: 'bg-red-100 border-red-200',
  B: 'bg-yellow-100 border-yellow-200',
  C: 'bg-green-100 border-green-200',
}

const LEVEL_LABELS = { 1: 'Techo', 2: 'Medio', 3: 'Piso' }
const ZONE_POR_NIVEL = { 3: 'A', 2: 'B', 1: 'C' }

function Celda({ code, producto, zona, seleccionado, onClick, isTop }) {
  const ocupada = !!producto
  const esSeleccionado = seleccionado?.position_code === code

  let colorClass = ''
  if (esSeleccionado) {
    colorClass = 'bg-blue-500 border-blue-600 ring-2 ring-blue-300 scale-125 z-10'
  } else if (ocupada) {
    colorClass = ZONE_COLORS[producto.abc_zone] || ZONE_COLORS[zona]
  } else {
    colorClass = ZONE_COLORS_EMPTY[zona]
  }

  // Si está en la parte superior mostrar tooltip abajo, si no arriba
  const tooltipPos = isTop
    ? 'top-full mt-1'
    : 'bottom-full mb-1'

  return (
    <div
      onClick={() => onClick(code, producto)}
      className={`w-5 h-5 rounded-sm border cursor-pointer transition hover:scale-110 relative group ${colorClass}`}
    >
      {ocupada && (
        <div className={`absolute left-1/2 -translate-x-1/2 hidden group-hover:block z-50 w-52 bg-gray-900 text-white text-xs rounded p-2 shadow-lg pointer-events-none ${tooltipPos}`}>
          <p className="font-bold text-blue-300">{code}</p>
          <p className="text-gray-300 text-xs">{producto.sku}</p>
          <p className="truncate">{producto.name}</p>
          <p className={`font-bold mt-1 ${
            producto.abc_zone === 'A' ? 'text-red-400' :
            producto.abc_zone === 'B' ? 'text-yellow-400' : 'text-green-400'
          }`}>Zona {producto.abc_zone}</p>
          <p className="text-gray-400 text-xs mt-1">Click para mover</p>
        </div>
      )}
      {!ocupada && seleccionado && (
        <div className={`absolute left-1/2 -translate-x-1/2 hidden group-hover:block z-50 w-40 bg-gray-900 text-white text-xs rounded p-2 shadow-lg pointer-events-none ${tooltipPos}`}>
          <p className="font-bold text-blue-300">{code}</p>
          <p className="text-green-400">Mover aquí →</p>
        </div>
      )}
    </div>
  )
}

function RackMap({ productos, onMapaActualizado }) {
  const [seleccionado, setSeleccionado] = useState(null)
  const [moviendo, setMoviendo]         = useState(false)

  // Construir mapa de posiciones
  const posicionMap = {}
  productos.forEach((p) => {
    if (p.position_code) posicionMap[p.position_code] = p
  })

  const totalOcupadas   = Object.keys(posicionMap).length
  const totalPosiciones = 384

  const handleCeldaClick = async (code, producto) => {
    // Si no hay seleccionado, seleccionar este (solo si está ocupado)
    if (!seleccionado) {
      if (producto) setSeleccionado(producto)
      return
    }

    // Si click en el mismo producto, deseleccionar
    if (seleccionado.position_code === code) {
      setSeleccionado(null)
      return
    }

    // Si click en celda ocupada diferente, cambiar selección
    if (producto) {
      setSeleccionado(producto)
      return
    }

    // Click en celda libre → mover el producto seleccionado aquí
    setMoviendo(true)
    try {
      await api.put(`/products/reasignar/${seleccionado.id}/${code}`)
      setSeleccionado(null)
      if (onMapaActualizado) onMapaActualizado()
    } catch (err) {
      alert('Error al mover el producto')
    } finally {
      setMoviendo(false)
    }
  }

  const racks = [
    { id: 1, porNivel: { 3: 27, 2: 27, 1: 26 } },
    { id: 2, porNivel: { 3: 27, 2: 27, 1: 26 } },
    { id: 3, porNivel: { 3: 27, 2: 27, 1: 26 } },
  ]

  return (
    <div className="bg-white rounded-xl shadow p-6">

      {/* Header con leyenda */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-700">
            Mapa de Racks — Sugerencia de Ubicación
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            {seleccionado
              ? `📦 Seleccionado: ${seleccionado.sku} — ${seleccionado.name} | Haz click en una celda libre para moverlo`
              : 'Haz click en una celda ocupada para seleccionar un producto y moverlo'}
          </p>
        </div>

        <div className="flex flex-col items-end gap-2">
          {/* Contador */}
          <span className="text-xs text-gray-400">
            {totalOcupadas} / {totalPosiciones} posiciones ocupadas
          </span>

          {/* Leyenda */}
          <div className="flex gap-3 flex-wrap justify-end">
            {[
              { label: 'Zona A — Piso', color: 'bg-red-500' },
              { label: 'Zona B — Medio', color: 'bg-yellow-400' },
              { label: 'Zona C — Techo', color: 'bg-green-500' },
              { label: 'Seleccionado', color: 'bg-blue-500' },
              { label: 'Libre', color: 'bg-gray-100 border border-gray-300' },
            ].map(({ label, color }) => (
              <div key={label} className="flex items-center gap-1">
                <div className={`w-3 h-3 rounded-sm ${color}`} />
                <span className="text-xs text-gray-500">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Indicador de movimiento */}
      {moviendo && (
        <div className="text-center text-blue-500 text-sm animate-pulse mb-4">
          Moviendo producto...
        </div>
      )}

      {/* Selección activa */}
      {seleccionado && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2 mb-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-blue-700">Moviendo: </span>
            <span className="text-xs text-blue-600">{seleccionado.sku} — {seleccionado.name}</span>
            <span className="text-xs text-blue-400 ml-2">desde {seleccionado.position_code}</span>
          </div>
          <button
            onClick={() => setSeleccionado(null)}
            className="text-xs text-blue-400 hover:text-blue-600"
          >
            Cancelar
          </button>
        </div>
      )}

      <div className="flex gap-6 overflow-x-auto pb-2">
        {/* Racks */}
        {racks.map((rack) => (
          <div key={rack.id} className="flex-1 min-w-[200px]">
            <h3 className="text-center font-bold text-gray-600 mb-3">Rack {rack.id}</h3>
            {[1, 2, 3].map((nivel) => {
              const zona    = ZONE_POR_NIVEL[nivel]
              const columnas = rack.porNivel[nivel]
              return (
                <div key={nivel} className="mb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400 w-10">{LEVEL_LABELS[nivel]}</span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${ZONE_COLORS[zona]}`}>
                      Zona {zona}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: columnas }).map((_, i) => {
                      const code    = `R${rack.id}-N${nivel}-C${i + 1}`
                      const producto = posicionMap[code]
                      return (
                        <Celda
                          key={i}
                          code={code}
                          producto={producto}
                          zona={zona}
                          seleccionado={seleccionado}
                          onClick={handleCeldaClick}
                          isTop={nivel === 1}
                        />
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        ))}

        {/* Islas */}
        <div className="flex-1 min-w-[200px]">
          <h3 className="text-center font-bold text-gray-600 mb-3">Islas</h3>
          {Array.from({ length: 9 }).map((_, islaIdx) => (
            <div key={islaIdx} className="mb-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-gray-400">Isla {islaIdx + 1}</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${ZONE_COLORS['A']}`}>
                  Zona A
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {Array.from({ length: 16 }).map((_, i) => {
                  const code     = `I${islaIdx + 1}-P${i + 1}`
                  const producto = posicionMap[code]
                  return (
                    <Celda
                      key={i}
                      code={code}
                      producto={producto}
                      zona="A"
                      seleccionado={seleccionado}
                      onClick={handleCeldaClick}
                        isTop={false}
                    />
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RackMap