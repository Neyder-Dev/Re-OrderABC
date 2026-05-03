function StatsBar({ stats }) {
  if (!stats) return null

  const zonas = [
    {
      zona: 'A',
      skus: stats.skus_zone_a,
      color: 'bg-red-500',
      texto: 'Alta rotación — Nivel piso',
    },
    {
      zona: 'B',
      skus: stats.skus_zone_b,
      color: 'bg-yellow-400',
      texto: 'Rotación media — Nivel medio',
    },
    {
      zona: 'C',
      skus: stats.skus_zone_c,
      color: 'bg-green-500',
      texto: 'Baja rotación — Nivel techo',
    },
  ]

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {zonas.map(({ zona, skus, color, texto }) => (
        <div key={zona} className="bg-white rounded-xl shadow p-4 flex items-center gap-4">
          <div className={`${color} text-white font-bold text-2xl w-12 h-12 rounded-lg flex items-center justify-center`}>
            {zona}
          </div>
          <div>
            <p className="text-3xl font-bold text-gray-800">{skus}</p>
            <p className="text-xs text-gray-500">{texto}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default StatsBar