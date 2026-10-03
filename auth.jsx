import { createContext, useContext, useState } from 'react'
import { api } from './api'

const AuthCtx = createContext(null)

function load() {
  try { return JSON.parse(localStorage.getItem('st_user')) } catch { return null }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(load)

  const save = data => {
    try {
      localStorage.setItem('st_token', data.access_token)
      localStorage.setItem('st_user', JSON.stringify(data.user))
    } catch {}
    setUser(data.user)
    return data.user
  }
  const login = async (email, password) => save(await api('/api/auth/login', { method: 'POST', body: { email, password } }))
  const register = async payload => save(await api('/api/auth/register', { method: 'POST', body: payload }))
  const logout = () => {
    try { localStorage.removeItem('st_token'); localStorage.removeItem('st_user') } catch {}
    setUser(null)
  }
  return <AuthCtx.Provider value={{ user, login, register, logout }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)
