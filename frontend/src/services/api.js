import axios from 'axios'
import useAuthStore from '../store/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Interceptor — agrega el token a cada request automáticamente
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor — si el token expira, hacer logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(error)
  }
)

export const loginApi = (email, password) =>
  api.post('/auth/login', { email, password })

export const uploadMatr780 = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/uploads/matr780', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const uploadMatr425 = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/inventory/upload-stock', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getMapa = () => api.get('/products/mapa')

export default api