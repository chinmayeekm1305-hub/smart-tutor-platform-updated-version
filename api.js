const BASE = import.meta.env.VITE_API_URL || ''

export function getToken() {
  try { return localStorage.getItem('st_token') } catch { return null }
}

export async function api(path, { method = 'GET', body, ...rest } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined, ...rest })
  if (res.status === 401 && token) {
    try { localStorage.removeItem('st_token'); localStorage.removeItem('st_user') } catch {}
    window.location.href = '/login'
    return
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const msg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail
    throw new Error(msg || `Request failed (${res.status})`)
  }
  return data
}

export const pct = (v, d = 0) => (v == null ? '—' : `${(v * 100).toFixed(d)}%`)
export const diffLabel = d => ({ 1: 'Easy', 2: 'Medium', 3: 'Hard' }[d] || d)
