'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { Brand } from '@/types'
import { LeanIndicator } from '@/components/LeanIndicator'

export default function RankingsPage() {
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)
  const [minVisits, setMinVisits] = useState(100000)

  useEffect(() => {
    fetch('/data/brands.json')
      .then(res => res.json())
      .then(data => {
        setBrands(data.brands)
        setLoading(false)
      })
  }, [])

  const filteredBrands = useMemo(() => {
    return brands.filter(b => b.lean_2020 !== null && b.total_visits >= minVisits)
  }, [brands, minVisits])

  const mostRepublican = useMemo(() => {
    return [...filteredBrands]
      .sort((a, b) => (b.lean_2020 || 0) - (a.lean_2020 || 0))
      .slice(0, 25)
  }, [filteredBrands])

  const mostDemocratic = useMemo(() => {
    return [...filteredBrands]
      .sort((a, b) => (a.lean_2020 || 0) - (b.lean_2020 || 0))
      .slice(0, 25)
  }, [filteredBrands])

  if (loading) {
    return (
      <div className="py-12 text-center">
        <p className="text-gray-500">Loading rankings...</p>
      </div>
    )
  }

  return (
    <div className="py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Rankings</h1>
        <p className="text-gray-500 mb-6">
          Brands with the most partisan customer bases
        </p>

        {/* Filter */}
        <div className="mb-6 flex items-center gap-4">
          <label className="text-sm text-gray-600">Minimum total visits:</label>
          <select
            value={minVisits}
            onChange={e => setMinVisits(Number(e.target.value))}
            className="border rounded px-3 py-1.5 text-sm"
          >
            <option value={10000}>10,000+</option>
            <option value={100000}>100,000+</option>
            <option value={500000}>500,000+</option>
            <option value={1000000}>1,000,000+</option>
          </select>
          <span className="text-sm text-gray-400">
            ({filteredBrands.length.toLocaleString()} brands)
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Most Republican */}
          <div>
            <h2 className="text-xl font-semibold text-republican-700 mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-republican-500" />
              Most Republican-Leaning
            </h2>
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-republican-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-republican-700 uppercase">#</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-republican-700 uppercase">Brand</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-republican-700 uppercase">Lean</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {mostRepublican.map((brand, i) => (
                    <tr key={brand.slug} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-500">{i + 1}</td>
                      <td className="px-4 py-2">
                        <Link
                          href={`/brands/${brand.slug}`}
                          className="text-sm font-medium text-gray-900 hover:text-republican-600"
                        >
                          {brand.name}
                        </Link>
                        <p className="text-xs text-gray-400">{brand.category}</p>
                      </td>
                      <td className="px-4 py-2">
                        <LeanIndicator lean={brand.lean_2020} size="sm" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Most Democratic */}
          <div>
            <h2 className="text-xl font-semibold text-democratic-700 mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-democratic-500" />
              Most Democratic-Leaning
            </h2>
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-democratic-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-democratic-700 uppercase">#</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-democratic-700 uppercase">Brand</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-democratic-700 uppercase">Lean</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {mostDemocratic.map((brand, i) => (
                    <tr key={brand.slug} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-500">{i + 1}</td>
                      <td className="px-4 py-2">
                        <Link
                          href={`/brands/${brand.slug}`}
                          className="text-sm font-medium text-gray-900 hover:text-democratic-600"
                        >
                          {brand.name}
                        </Link>
                        <p className="text-xs text-gray-400">{brand.category}</p>
                      </td>
                      <td className="px-4 py-2">
                        <LeanIndicator lean={brand.lean_2020} size="sm" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Note */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
          <p>
            <strong>Note:</strong> Rankings show brands with at least {minVisits.toLocaleString()} total
            visits across the observation period. Partisan lean is calculated as the estimated two-party
            Republican vote share among visitors based on their home census block group.
          </p>
        </div>
      </div>
    </div>
  )
}
