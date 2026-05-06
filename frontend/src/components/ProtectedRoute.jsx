import useAuthStore from '../store/authStore'
import Login from '../pages/Login'

function ProtectedRoute({ children, soloJefe = false }) {
  const token   = useAuthStore((s) => s.token)
  const usuario = useAuthStore((s) => s.usuario)

  if (!token) return <Login />

  if (soloJefe && usuario?.rol !== 'jefe') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-400">
          <p className="text-5xl mb-4">🔒</p>
          <p className="text-lg font-medium">Acceso restringido</p>
          <p className="text-sm mt-2">Solo el jefe puede acceder a esta sección</p>
        </div>
      </div>
    )
  }

  return children
}

export default ProtectedRoute