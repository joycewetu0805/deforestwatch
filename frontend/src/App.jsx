import { useState } from 'react'
import LandingPage from './components/LandingPage.jsx'
import Dashboard from './components/Dashboard.jsx'

export default function App() {
  const [view, setView] = useState('landing')
  return view === 'landing'
    ? <LandingPage onExplore={() => setView('dashboard')} />
    : <Dashboard onBack={() => setView('landing')} />
}
