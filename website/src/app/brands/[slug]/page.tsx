import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Building2, MapPin, Calendar, TrendingUp } from 'lucide-react'
import { getBrands, getBrandTimeSeries } from '@/lib/data'
import { LeanIndicator, LeanBadge } from '@/components/LeanIndicator'
import { TimeSeriesChart } from '@/components/TimeSeriesChart'

interface PageProps {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  const { brands } = await getBrands()
  return brands.map(brand => ({ slug: brand.slug }))
}

export default async function BrandPage({ params }: PageProps) {
  const { slug } = await params
  const { brands } = await getBrands()
  const brand = brands.find(b => b.slug === slug)

  if (!brand) {
    notFound()
  }

  const timeSeries = await getBrandTimeSeries(slug)

  return (
    <div className="py-8">
      <div className="max-w-5xl mx-auto px-4">
        <Link
          href="/brands"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to all brands
        </Link>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{brand.name}</h1>
              {brand.company && brand.company !== brand.name && (
                <p className="text-gray-500 mt-1">{brand.company}</p>
              )}
              {brand.ticker && (
                <p className="text-sm text-gray-400 mt-1">NYSE: {brand.ticker}</p>
              )}
            </div>
            <div className="flex flex-col items-end gap-2">
              <LeanBadge lean={brand.lean_2020} />
              <LeanIndicator lean={brand.lean_2020} size="lg" />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Category</p>
                <p className="font-medium">{brand.category || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Avg. Locations</p>
                <p className="font-medium">{brand.avg_locations?.toLocaleString() || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Months of Data</p>
                <p className="font-medium">{brand.n_months}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Total Visits</p>
                <p className="font-medium">{brand.total_visits.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Time Series */}
        {timeSeries && timeSeries.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Partisan Lean Over Time</h2>
            <TimeSeriesChart data={timeSeries} />
          </div>
        )}

        {/* Lean Details */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Lean Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">2020 Election Baseline</h3>
              <p className="text-2xl font-bold">
                {brand.lean_2020 !== null ? `${(brand.lean_2020 * 100).toFixed(1)}%` : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Two-party Republican vote share</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">2016 Election Baseline</h3>
              <p className="text-2xl font-bold">
                {brand.lean_2016 !== null ? `${(brand.lean_2016 * 100).toFixed(1)}%` : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Two-party Republican vote share</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Standard Deviation</h3>
              <p className="text-2xl font-bold">
                {brand.lean_std !== null ? `${(brand.lean_std * 100).toFixed(2)}%` : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Variation across months</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Geographic Coverage</h3>
              <p className="text-2xl font-bold">
                {brand.avg_states !== null ? `${Math.round(brand.avg_states)} states` : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Average states with presence</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
