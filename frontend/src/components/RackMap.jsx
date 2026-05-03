const ZONE_COLORS = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-400 text-gray-800',
  C: 'bg-green-500 text-white',
  null: 'bg-gray-100 text-gray-400',
}

const LEVEL_LABELS = {
  1: 'Techo',
  2: 'Medio',
  3: 'Piso',
}

function RackMap({ productos }) {
  // Agrupar productos por zona
  const porZona = { A: [], B: [], C: [] }
  productos.forEach((p) => {
    if (porZona[p.abc_zone]) porZona[p.abc_zone].push(p)
  })

  // Generar posiciones de los 3 racks (27, 27, 26 por nivel)
  const racks = [
    { id: 1, porNivel: [27, 27, 26] },
    { id: 2, porNivel: [27, 27, 26] },
    { id: 3, porNivel: [27, 27, 26] },
  ]

  // Asignar zona sugerida por nivel
  // Nivel 3 (piso) → A, Nivel 2 (medio) → B, Nivel 1 (techo) → C
  const zonaPorNivel = { 3: 'A', 2: 'B', 1: 'C' }

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">
        Mapa de Racks — Sugerencia de Ubicación
      </h2>
      <p className="text-xs text-gray-400 mb-6">
        Cada celda representa una posición. El color indica la zona ABC sugerida según el nivel.
      </p>

      <div className="flex gap-6 overflow-x-auto pb-2">
        {racks.map((rack) => (
          <div key={rack.id} className="flex-1 min-w-[200px]">
            <h3 className="text-center font-bold text-gray-600 mb-3">
              Rack {rack.id}
            </h3>

            {[1, 2, 3].map((nivel) => {
              const zona = zonaPorNivel[nivel]
              const posiciones = rack.porNivel[nivel - 1]

              return (
                <div key={nivel} className="mb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400 w-10">
                      {LEVEL_LABELS[nivel]}
                    </span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${ZONE_COLORS[zona]}`}>
                      Zona {zona}
                    </span>
                    <span className="text-xs text-gray-300">
                      {posiciones} pos.
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: posiciones }).map((_, i) => (
                      <div
                        key={i}
                        className={`w-5 h-5 rounded-sm ${ZONE_COLORS[zona]} opacity-80 hover:opacity-100 transition cursor-pointer`}
                        title={`R${rack.id}-N${nivel}-C${i + 1} | Zona ${zona}`}
                      />
                    ))}
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
                {Array.from({ length: 16 }).map((_, i) => (
                  <div
                    key={i}
                    className={`w-5 h-5 rounded-sm ${ZONE_COLORS['A']} opacity-80 hover:opacity-100 transition cursor-pointer`}
                    title={`Isla ${islaIdx + 1} - Pos ${i + 1} | Zona A`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leyenda */}
      <div className="flex gap-4 mt-6 pt-4 border-t border-gray-100">
        {[
          { zona: 'A', label: 'Alta rotación — Piso', color: 'bg-red-500' },
          { zona: 'B', label: 'Rotación media — Medio', color: 'bg-yellow-400' },
          { zona: 'C', label: 'Baja rotación — Techo', color: 'bg-green-500' },
        ].map(({ zona, label, color }) => (
          <div key={zona} className="flex items-center gap-2">
            <div className={`w-4 h-4 rounded-sm ${color}`} />
            <span className="text-xs text-gray-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RackMap