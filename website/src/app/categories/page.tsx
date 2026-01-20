'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { Category } from '@/types'
import { LeanIndicator } from '@/components/LeanIndicator'

const NAICS_NAMES: Record<string, string> = {
  '11': 'Agriculture, Forestry, Fishing',
  '21': 'Mining, Oil & Gas',
  '22': 'Utilities',
  '23': 'Construction',
  '31': 'Manufacturing - Food & Textile',
  '32': 'Manufacturing - Wood, Paper, Chemical',
  '33': 'Manufacturing - Metal, Machinery, Electronics',
  '42': 'Wholesale Trade',
  '44': 'Retail Trade - Motor, Furniture, Electronics',
  '45': 'Retail Trade - General, Food, Health',
  '48': 'Transportation & Warehousing',
  '49': 'Transportation - Postal & Courier',
  '51': 'Information',
  '52': 'Finance & Insurance',
  '53': 'Real Estate',
  '54': 'Professional Services',
  '55': 'Management of Companies',
  '56': 'Administrative Services',
  '61': 'Educational Services',
  '62': 'Health Care & Social Assistance',
  '71': 'Arts, Entertainment, Recreation',
  '72': 'Accommodation & Food Services',
  '81': 'Other Services',
  '92': 'Public Administration',
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Record<string, Category>>({})
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetch('/data/categories.json')
      .then(res => res.json())
      .then(data => {
        setCategories(data)
        setLoading(false)
      })
  }, [])

  const toggleExpand = (code: string) => {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(code)) {
        next.delete(code)
      } else {
        next.add(code)
      }
      return next
    })
  }

  if (loading) {
    return (
      <div className="py-12 text-center">
        <p className="text-gray-500">Loading categories...</p>
      </div>
    )
  }

  const sortedCategories = Object.entries(categories).sort(([a], [b]) => a.localeCompare(b))

  return (
    <div className="py-8">
      <div className="max-w-5xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Categories</h1>
        <p className="text-gray-500 mb-6">
          Browse brands by NAICS industry classification
        </p>

        <div className="space-y-2">
          {sortedCategories.map(([code, category]) => {
            const isExpanded = expanded.has(code)
            const name = NAICS_NAMES[code] || `NAICS ${code}`

            return (
              <div key={code} className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <button
                  onClick={() => toggleExpand(code)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    )}
                    <div className="text-left">
                      <span className="font-medium text-gray-900">{name}</span>
                      <span className="text-sm text-gray-400 ml-2">({code})</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-500">
                      {category.stats?.n_brands || 0} brands
                    </span>
                    {category.stats?.mean_lean !== undefined && (
                      <LeanIndicator lean={category.stats.mean_lean} size="sm" showLabel={false} />
                    )}
                  </div>
                </button>

                {isExpanded && (
                  <div className="border-t px-4 py-3 bg-gray-50">
                    {category.stats && (
                      <div className="flex items-center gap-6 mb-4 text-sm">
                        <span>
                          Mean lean: <strong>{(category.stats.mean_lean * 100).toFixed(1)}%</strong>
                        </span>
                        <span className="text-gray-400">|</span>
                        <span>
                          Range: {(category.stats.min_lean * 100).toFixed(1)}% - {(category.stats.max_lean * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                      {category.brands
                        .sort((a, b) => (a.lean_2020 || 0.5) - (b.lean_2020 || 0.5))
                        .slice(0, 20)
                        .map(brand => (
                          <Link
                            key={brand.name}
                            href={`/brands/${brand.name.toLowerCase().replace(/ /g, '-').replace(/'/g, '')}`}
                            className="text-sm text-blue-600 hover:text-blue-800 truncate"
                          >
                            {brand.name}
                          </Link>
                        ))}
                      {category.brands.length > 20 && (
                        <span className="text-sm text-gray-400">
                          +{category.brands.length - 20} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
