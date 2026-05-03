import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export const uploadMatr780 = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/uploads/matr780', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export default api