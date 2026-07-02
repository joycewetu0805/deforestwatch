import { useState } from 'react'
import LandingPage from './components/LandingPage.jsx'
import Dashboard from './components/Dashboard.jsx'
import Login from './components/Login.jsx'

function loadAuth() {
  try {
    const token = localStorage.getItem('dfw_token')
    const user = JSON.parse(localStorage.getItem('dfw_user') || 'null')
    return token && user ? { token, user } : null
  } catch {
    return null
  }
}

export default function App() {
  const [view, setView] = useState('landing')
  const [auth, setAuth] = useState(loadAuth)

  const openDashboard = () => setView(auth ? 'dashboard' : 'login')

  const onLoginSuccess = (a) => {
    setAuth(a)
    setView('dashboard')
  }

  const logout = () => {
    localStorage.removeItem('dfw_token')
    localStorage.removeItem('dfw_user')
    setAuth(null)
    setView('landing')
  }

  if (view === 'login') {
    return <Login onSuccess={onLoginSuccess} onBack={() => setView('landing')} />
  }
  if (view === 'dashboard' && auth) {
    return <Dashboard user={auth.user} onBack={() => setView('landing')} onLogout={logout} />
  }
  return <LandingPage onExplore={openDashboard} />
}
