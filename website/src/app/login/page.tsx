'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Lock } from 'lucide-react'

function LoginForm() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })

      if (res.ok) {
        const from = searchParams.get('from') || '/'
        router.push(from)
        router.refresh()
      } else {
        setError('Invalid password')
      }
    } catch {
      setError('An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow-sm rounded-lg border p-6">
      <div className="mb-4">
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter password"
          required
        />
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Verifying...' : 'Access Data'}
      </button>
    </form>
  )
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Lock className="w-6 h-6 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Brand Partisan Lean Explorer</h1>
          <p className="text-gray-500 mt-2">Enter the password to access the research data</p>
        </div>

        <Suspense fallback={
          <div className="bg-white shadow-sm rounded-lg border p-6 animate-pulse">
            <div className="h-10 bg-gray-200 rounded mb-4"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        }>
          <LoginForm />
        </Suspense>

        <p className="text-center text-sm text-gray-500 mt-6">
          Need access?{' '}
          <a href="mailto:maxkagan@berkeley.edu" className="text-blue-600 hover:underline">
            Contact the research team
          </a>
        </p>
      </div>
    </div>
  )
}
