'use client'

import { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { TimeSeriesPoint } from '@/types'

interface TimeSeriesChartProps {
  data: TimeSeriesPoint[]
}

export function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  const [metric, setMetric] = useState<'lean_2020' | 'lean_2016'>('lean_2020')

  const chartData = data
    .filter(d => d[metric] !== null)
    .map(d => ({
      month: d.month,
      lean: d[metric]! * 100,
      visits: d.visits,
    }))

  const minLean = Math.min(...chartData.map(d => d.lean))
  const maxLean = Math.max(...chartData.map(d => d.lean))
  const yMin = Math.floor(Math.min(minLean, 45) / 5) * 5
  const yMax = Math.ceil(Math.max(maxLean, 55) / 5) * 5

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <label className="text-sm text-gray-500">Election baseline:</label>
        <select
          value={metric}
          onChange={e => setMetric(e.target.value as 'lean_2020' | 'lean_2016')}
          className="text-sm border rounded px-2 py-1"
        >
          <option value="lean_2020">2020 Election</option>
          <option value="lean_2016">2016 Election</option>
        </select>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 11 }}
              tickFormatter={val => {
                const [year, month] = val.split('-')
                return month === '01' ? year : ''
              }}
              stroke="#9ca3af"
            />
            <YAxis
              domain={[yMin, yMax]}
              tick={{ fontSize: 11 }}
              tickFormatter={val => `${val}%`}
              stroke="#9ca3af"
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0].payload
                return (
                  <div className="bg-white border rounded-lg shadow-lg p-3 text-sm">
                    <p className="font-medium">{d.month}</p>
                    <p className="text-gray-600">
                      Lean: <span className="font-medium">{d.lean.toFixed(1)}% R</span>
                    </p>
                    <p className="text-gray-500 text-xs">
                      {d.visits.toLocaleString()} visits
                    </p>
                  </div>
                )
              }}
            />
            <ReferenceLine y={50} stroke="#9ca3af" strokeDasharray="5 5" />
            <Line
              type="monotone"
              dataKey="lean"
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#6366f1' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-center gap-6 mt-4 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <div className="w-8 h-0.5 bg-gray-400" style={{ borderStyle: 'dashed' }} />
          <span>50% = Balanced</span>
        </div>
        <div className="flex items-center gap-1">
          <span>&lt;50% = More Democratic</span>
        </div>
        <div className="flex items-center gap-1">
          <span>&gt;50% = More Republican</span>
        </div>
      </div>
    </div>
  )
}
