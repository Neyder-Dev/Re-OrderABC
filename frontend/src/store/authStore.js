import { create } from 'zustand'

const useAuthStore = create((set) => ({
  token: null,
  usuario: null,

  login: (token, usuario) => set({ token, usuario }),
  logout: () => set({ token: null, usuario: null }),

  isAuthenticated: () => {
    const state = useAuthStore.getState()
    return !!state.token
  },

  isJefe: () => {
    const state = useAuthStore.getState()
    return state.usuario?.rol === 'jefe'
  },
}))

export default useAuthStore