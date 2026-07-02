import { useState } from 'react'
import { Leaf, Lock, ArrowLeft, ShieldCheck } from 'lucide-react'

// Comptes de démo (utilisés si l'API n'est pas joignable — build statique Vercel)
const DEMO = {
  'admin@deforestwatch.cd': { password: 'admin123', role: 'admin', name: 'Administrateur' },
  'user@deforestwatch.cd': { password: 'user123', role: 'user', name: 'Analyste' },
}
const DEMO_OTP = '123456'

async function apiLogin(email, password) {
  const r = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!r.ok) throw new Error('api')
  return r.json() // { access_token, ... }
}

export default function Login({ onSuccess, onBack }) {
  const [email, setEmail] = useState('admin@deforestwatch.cd')
  const [password, setPassword] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (otp !== DEMO_OTP && !/^\d{6}$/.test(otp)) {
      setError('Entrez le code 2FA à 6 chiffres (démo : 123456).')
      return
    }
    setLoading(true)
    try {
      // 1) tente l'API réelle (JWT)
      let token = null
      let user = { email, role: 'user', name: email.split('@')[0] }
      try {
        const data = await apiLogin(email, password)
        token = data.access_token
        user.role = 'user'
      } catch {
        // 2) repli démo (build statique sans backend)
        const u = DEMO[email]
        if (!u || u.password !== password) throw new Error('Identifiants invalides.')
        if (otp !== DEMO_OTP) throw new Error('Code 2FA invalide.')
        token = 'demo-token'
        user = { email, role: u.role, name: u.name }
      }
      localStorage.setItem('dfw_token', token)
      localStorage.setItem('dfw_user', JSON.stringify(user))
      onSuccess({ token, user })
    } catch (err) {
      setError(err.message || 'Échec de la connexion.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-6 text-slate-200">
      <div className="pointer-events-none absolute inset-0 opacity-40"
        style={{ background: 'radial-gradient(circle at 30% 20%, rgba(16,185,129,0.22), transparent 45%), radial-gradient(circle at 75% 70%, rgba(6,182,212,0.16), transparent 42%)' }} />
      <div className="relative w-full max-w-md">
        <button onClick={onBack}
          className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-glow">
          <ArrowLeft size={16} /> Retour à l'accueil
        </button>

        <div className="rounded-2xl border border-white/10 bg-panel/70 p-8 backdrop-blur-md">
          <div className="mb-6 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-glow/15 text-emerald-glow">
              <Leaf size={24} />
            </div>
            <h1 className="mt-3 text-2xl font-bold text-emerald-glow">CongoForest Watch</h1>
            <p className="text-sm text-slate-400">Connexion sécurisée (2FA)</p>
          </div>

          <form onSubmit={submit} className="space-y-4">
            <Field label="Email" type="email" value={email} onChange={setEmail} icon={null} />
            <Field label="Mot de passe" type="password" value={password} onChange={setPassword}
              placeholder="admin123" icon={<Lock size={15} />} />
            <Field label="Code 2FA (Google Authenticator)" type="text" value={otp}
              onChange={setOtp} placeholder="123456" maxLength={6} icon={<ShieldCheck size={15} />} />

            {error && <p className="text-sm text-alert">{error}</p>}

            <button type="submit" disabled={loading}
              className="w-full rounded-xl bg-emerald-glow py-3 font-semibold text-[#04130c]
                         transition hover:scale-[1.02] disabled:opacity-60">
              {loading ? 'Connexion…' : 'Se connecter'}
            </button>
          </form>

          <p className="mt-5 text-center text-xs text-slate-500">
            Démo : admin@deforestwatch.cd / admin123 · code 2FA : 123456
          </p>
        </div>
      </div>
    </div>
  )
}

function Field({ label, icon, ...props }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-slate-400">{label}</span>
      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-base/60 px-3 focus-within:border-emerald-glow/50">
        {icon && <span className="text-slate-500">{icon}</span>}
        <input {...props} onChange={(e) => props.onChange(e.target.value)}
          className="w-full bg-transparent py-2.5 text-sm text-slate-100 outline-none" required />
      </div>
    </label>
  )
}
