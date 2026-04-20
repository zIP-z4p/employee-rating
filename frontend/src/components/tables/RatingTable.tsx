import React, { useState } from 'react'
import { RatingSnapshot } from '../../api/client'

interface Props {
  snapshots: RatingSnapshot[]
  period: string
}

const DeltaBadge: React.FC<{ value: number | null }> = ({ value }) => {
  if (value === null) return <span style={{ color: '#64748b' }}>—</span>
  const isPositive = value >= 0
  return (
    <span style={{ color: isPositive ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
      {isPositive ? '▲' : '▼'} {Math.abs(value).toFixed(2)}
    </span>
  )
}

export const RatingTable: React.FC<Props> = ({ snapshots, period }) => {
  const [sortField, setSortField] = useState<keyof RatingSnapshot>('rank')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const sorted = [...snapshots].sort((a, b) => {
    const av = a[sortField] as number
    const bv = b[sortField] as number
    return sortDir === 'asc' ? av - bv : bv - av
  })

  const toggleSort = (field: keyof RatingSnapshot) => {
    if (field === sortField) {
      setSortDir(prev => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const columns = [
    { key: 'rank', label: '#', sortable: true },
    { key: 'employee_name', label: 'Employee', sortable: false },
    { key: 'department_name', label: 'Department', sortable: false },
    { key: 'total_score', label: 'Score', sortable: true },
    { key: 'percentile', label: 'Percentile', sortable: true },
    { key: 'delta_score', label: 'Δ Score', sortable: false },
    { key: 'delta_rank', label: 'Δ Rank', sortable: false },
  ]

  if (snapshots.length === 0) {
    return (
      <p style={{ color: '#94a3b8', textAlign: 'center', padding: 40 }}>
        No data for period: {period}
      </p>
    )
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <h3 style={{ marginBottom: 12, color: '#f1f5f9' }}>
        Rating Snapshot — {period}
      </h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#1e293b' }}>
            {columns.map(col => (
              <th
                key={col.key}
                onClick={() =>
                  col.sortable && toggleSort(col.key as keyof RatingSnapshot)
                }
                style={{
                  padding: '10px 16px',
                  textAlign: 'left',
                  color: '#94a3b8',
                  fontWeight: 600,
                  cursor: col.sortable ? 'pointer' : 'default',
                  userSelect: 'none',
                  borderBottom: '2px solid #334155',
                }}
              >
                {col.label}{' '}
                {col.sortable && sortField === col.key
                  ? sortDir === 'asc'
                    ? '↑'
                    : '↓'
                  : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, idx) => (
            <tr
              key={row.employee_id}
              style={{ background: idx % 2 === 0 ? '#0f172a' : '#1e293b' }}
            >
              <td style={{ padding: '10px 16px', color: '#f1f5f9', fontWeight: 700 }}>
                {row.rank <= 3 ? ['🥇', '🥈', '🥉'][row.rank - 1] : row.rank}
              </td>
              <td style={{ padding: '10px 16px', color: '#f1f5f9' }}>
                {row.employee_name}
              </td>
              <td style={{ padding: '10px 16px', color: '#94a3b8' }}>
                {row.department_name}
              </td>
              <td style={{ padding: '10px 16px', color: '#6366f1', fontWeight: 600 }}>
                {Number(row.total_score).toFixed(2)}
              </td>
              <td style={{ padding: '10px 16px', color: '#94a3b8' }}>
                {Number(row.percentile).toFixed(1)}%
              </td>
              <td style={{ padding: '10px 16px' }}>
                <DeltaBadge value={row.delta_score} />
              </td>
              <td style={{ padding: '10px 16px' }}>
                <DeltaBadge value={row.delta_rank} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RatingTable

