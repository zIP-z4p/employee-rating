import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ratingsApi } from '../api/client'
import { RatingTable } from '../components/tables/RatingTable'
import { RatingTrendChart } from '../components/charts/RatingTrendChart'

export const Dashboard: React.FC = () => {
  const [period, setPeriod] = useState('2024-01-01')
  const [selectedEmployee, setSelectedEmployee] = useState<string | null>(null)

  const {
    data: snapshots,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['snapshots', period],
    queryFn: () => ratingsApi.getSnapshot(period).then(r => r.data),
  })

  const { data: trendData } = useQuery({
    queryKey: ['trend', selectedEmployee],
    queryFn: () =>
      ratingsApi.getEmployeeTrend(selectedEmployee!, 6).then(r => r.data),
    enabled: !!selectedEmployee,
  })

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 24 }}>
        📊 Employee Rating Dashboard
      </h1>

      <div style={{ marginBottom: 24, display: 'flex', gap: 12, alignItems: 'center' }}>
        <label style={{ color: '#94a3b8' }}>Period:</label>
        <input
          type="month"
          value={period.slice(0, 7)}
          onChange={e => setPeriod(e.target.value + '-01')}
          style={{
            background: '#1e293b',
            border: '1px solid #334155',
            color: '#f1f5f9',
            padding: '6px 12px',
            borderRadius: 6,
          }}
        />
        <button
          onClick={() =>
            ratingsApi.buildSnapshot(period).then(() => window.location.reload())
          }
          style={{
            background: '#6366f1',
            color: 'white',
            border: 'none',
            padding: '6px 16px',
            borderRadius: 6,
            cursor: 'pointer',
          }}
        >
          Build Snapshot
        </button>
      </div>

      <div
        style={{
          background: '#1e293b',
          borderRadius: 12,
          padding: 24,
          marginBottom: 24,
          border: '1px solid #334155',
        }}
      >
        {isLoading && <p style={{ color: '#94a3b8' }}>Loading...</p>}
        {error && (
          <p style={{ color: '#ef4444' }}>
            Error loading data. Make sure backend is running.
          </p>
        )}
        {snapshots && (
          <RatingTable snapshots={snapshots} period={period} />
        )}
      </div>

      {trendData && trendData.trend && (
        <div
          style={{
            background: '#1e293b',
            borderRadius: 12,
            padding: 24,
            border: '1px solid #334155',
          }}
        >
          <RatingTrendChart
            data={trendData.trend}
            employeeName={trendData.employee_name}
          />
        </div>
      )}
    </div>
  )
}

export default Dashboard

