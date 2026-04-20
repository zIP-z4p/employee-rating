import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from 'recharts'
import { TrendPoint } from '../../api/client'

interface Props {
  data: TrendPoint[]
  employeeName: string
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as TrendPoint
  const deltaColor = (d.delta_score ?? 0) >= 0 ? '#22c55e' : '#ef4444'
  const deltaSign = (d.delta_score ?? 0) >= 0 ? '+' : ''

  return (
    <div
      style={{
        background: '#1e293b',
        border: '1px solid #334155',
        padding: '12px',
        borderRadius: '8px',
        color: '#f1f5f9',
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: 4 }}>{d.period}</p>
      <p>Score: <strong>{Number(d.total_score).toFixed(2)}</strong></p>
      <p>Rank: <strong>#{d.rank}</strong></p>
      <p>Percentile: <strong>{d.percentile}%</strong></p>
      {d.delta_score !== null && (
        <p style={{ color: deltaColor }}>
          Delta: <strong>{deltaSign}{Number(d.delta_score).toFixed(2)}</strong>
        </p>
      )}
    </div>
  )
}

export const RatingTrendChart: React.FC<Props> = ({ data, employeeName }) => {
  const avgScore =
    data.length > 0
      ? data.reduce((s, p) => s + Number(p.total_score), 0) / data.length
      : 0

  return (
    <div style={{ width: '100%', height: 320 }}>
      <h3 style={{ marginBottom: 16, color: '#f1f5f9' }}>
        Rating Trend — {employeeName}
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="period"
            tick={{ fill: '#94a3b8' }}
            tickFormatter={(v: string) => v.slice(0, 7)}
          />
          <YAxis
            domain={[0, 10]}
            tick={{ fill: '#94a3b8' }}
            tickFormatter={(v: number) => v.toFixed(1)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <ReferenceLine
            y={avgScore}
            stroke="#f59e0b"
            strokeDasharray="4 4"
            label={{ value: `Avg: ${avgScore.toFixed(2)}`, fill: '#f59e0b' }}
          />
          <Line
            type="monotone"
            dataKey="total_score"
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ fill: '#6366f1', r: 5 }}
            activeDot={{ r: 8, fill: '#a78bfa' }}
            name="Total Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default RatingTrendChart

