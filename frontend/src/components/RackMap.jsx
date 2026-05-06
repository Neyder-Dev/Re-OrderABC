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

function RackMap({ productos }) {
  // Construir mapa de posiciones ocupadas
  const posicionMap = {}
  productos.forEach((p) => {
    if (p.position_code) {
      posicionMap[p.position_code] = p
    }
  })

  const racks = [
    { id: 1, porNivel: { 3: 27, 2: 27, 1: 26 } },
    { id: 2, porNivel: { 3: 27, 2: 27, 1: 26 } },
    { id: 3, porNivel: { 3: 27, 2: 27, 1: 26 } },
  ]

  const totalOcupadas = Object.keys(posicionMap).length
  const totalPosiciones = 384

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold text-gray-700">
          Mapa de Racks — Sugerencia de Ubicación
        </h2>
        <span className="text-xs text-gray-400">
          {totalOcupadas} / {totalPosiciones} posiciones ocupadas
        </span>
      </div>
      <p className="text-xs text-gray-400 mb-6">
        Pasa el cursor sobre una celda para ver el producto asignado.
        Celdas claras = posiciones libres.
      </p>

      <div className="flex gap-6 overflow-x-auto pb-2">
        {/* Racks */}
        {racks.map((rack) => (
          <div key={rack.id} className="flex-1 min-w-[200px]">
            <h3 className="text-center font-bold text-gray-600 mb-3">
              Rack {rack.id}
            </h3>

            {[1, 2, 3].map((nivel) => {
              const zona = ZONE_POR_NIVEL[nivel]
              const columnas = rack.porNivel[nivel]

              return (
                <div key={nivel} className="mb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400 w-10">
                      {LEVEL_LABELS[nivel]}
                    </span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${ZONE_COLORS[zona]}`}>
                      Zona {zona}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: columnas }).map((_, i) => {
                      const code = `R${rack.id}-N${nivel}-C${i + 1}`
                      const producto = posicionMap[code]

                      return (
                        <div
                          key={i}
                          className={`w-5 h-5 rounded-sm border cursor-pointer transition hover:scale-125 hover:z-10 relative group
                            ${producto ? ZONE_COLORS[zona] : ZONE_COLORS_EMPTY[zona]}`}
                          title={producto
                            ? `${code}\n${producto.sku}\n${producto.name}`
                            : `${code} — Libre`}
                        >
                          {/* Tooltip */}
                          {producto && (
                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-50 w-48 bg-gray-900 text-white text-xs rounded p-2 shadow-lg pointer-events-none">
                              <p className="font-bold">{code}</p>
                              <p className="text-gray-300">{producto.sku}</p>
                              <p className="truncate">{producto.name}</p>
                              <p className={`font-bold mt-1 ${
                                producto.abc_zone === 'A' ? 'text-red-400' :
                                producto.abc_zone === 'B' ? 'text-yellow-400' : 'text-green-400'
                              }`}>Zona {producto.abc_zone}</p>
                            </div>
                          )}
                        </div>
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
                  const code = `I${islaIdx + 1}-P${i + 1}`
                  const producto = posicionMap[code]

                  return (
                    <div
                      key={i}
                      className={`w-5 h-5 rounded-sm border cursor-pointer transition hover:scale-125 hover:z-10 relative group
                        ${producto ? ZONE_COLORS['A'] : ZONE_COLORS_EMPTY['A']}`}
                      title={producto
                        ? `${code}\n${producto.sku}\n${producto.name}`
                        : `${code} — Libre`}
                    >
                      {producto && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-50 w-48 bg-gray-900 text-white text-xs rounded p-2 shadow-lg pointer-events-none">
                          <p className="font-bold">{code}</p>
                          <p className="text-gray-300">{producto.sku}</p>
                          <p className="truncate">{producto.name}</p>
                          <p className="font-bold mt-1 text-red-400">Zona A</p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leyenda */}
      <div className="flex gap-6 mt-6 pt-4 border-t border-gray-100 flex-wrap">
        {[
          { label: 'Zona A ocupada', color: 'bg-red-500' },
          { label: 'Zona B ocupada', color: 'bg-yellow-400' },
          { label: 'Zona C ocupada', color: 'bg-green-500' },
          { label: 'Posición libre', color: 'bg-gray-100 border border-gray-300' },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-2">
            <div className={`w-4 h-4 rounded-sm ${color}`} />
            <span className="text-xs text-gray-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RackMap