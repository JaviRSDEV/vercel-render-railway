import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
})

// --- INTERCEPTOR DE SEGURIDAD ---
// Este bloque es vital: antes de cada petición, revisa si hay un token y lo pega
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const apiService = {
  // --- NUEVA FUNCIÓN: REGISTRO ---
  async register(payload: { username: string; password: str }) {
    try {
      const response = await api.post('/api/auth/register', payload)
      return response.data
    } catch (error) {
      console.error('Error en registro, este es el error:', error)
      throw error
    }
  },

  // --- NUEVA FUNCIÓN: LOGIN ---
  async login(username: string, password: str) {
    try {
      // FastAPI espera OAuth2PasswordRequestForm (form-data), no JSON
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/token', formData)
      return response.data // Devuelve { access_token: "...", token_type: "bearer" }
    } catch (error) {
      console.error('Error en login:', error)
      throw error
    }
  },

  async getStatus() {
    try {
      const response = await api.get('/')
      return response.data
    } catch (error) {
      console.error('Error fetching status:', error)
      throw error
    }
  },

  async getData() {
    try {
      const response = await api.get('/api/data')
      return response.data
    } catch (error) {
      console.error('Error fetching data:', error)
      throw error
    }
  },

  async listItems() {
    try {
      const response = await api.get('/api/items')
      return response.data
    } catch (error) {
      console.error('Error fetching items:', error)
      throw error
    }
  },

  async createItem(payload: { name: string; status: string }) {
    try {
      const response = await api.post('/api/items', payload)
      return response.data
    } catch (error) {
      console.error('Error creating item:', error)
      throw error
    }
  },

  async updateItem(itemId: number, payload: { name?: string; status?: string }) {
    try {
      const response = await api.put(`/api/items/${itemId}`, payload)
      return response.data
    } catch (error) {
      console.error('Error updating item:', error)
      throw error
    }
  },

  async deleteItem(itemId: number) {
    try {
      await api.delete(`/api/items/${itemId}`)
      return true
    } catch (error) {
      console.error('Error deleting item:', error)
      throw error
    }
  },
}

export default api