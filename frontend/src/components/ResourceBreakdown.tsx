import { useGeos } from '../hooks/useGeos'

export default function ResourceBreakdown() {
  const { data } = useGeos<{ total_nrv: number; details: Record<string, number> }>('/resources/nrv/total')

  if (!data) return null

  const entries = Object.entries(data.details).sort((a, b) => b[1] - a[1])
  const max = Math.max(...entries.map(([, v]) => v))

  return (
    <div>
      {entries.map(([name, nrv]) => (
        <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 14, marginBottom: 4 }}>{name}</div>
            <div style={{ height: 8, background: '#1e293b', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${(nrv / max) * 100}%`,
                background: 'linear-gradient(90deg, #3b82f6, #06b6d4)',
                borderRadius: 4,
                transition: 'width 0.5s',
              }} />
            </div>
          </div>
          <span style={{ fontSize: 14, fontWeight: 600, width: 80, textAlign: 'right', color: '#06b6d4' }}>
            {nrv.toLocaleString()} M
          </span>
        </div>
      ))}
      <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between' }}>
        <span style={{ color: '#94a3b8', fontSize: 14 }}>Total NRV</span>
        <span style={{ fontWeight: 700, color: '#06b6d4' }}>{data.total_nrv.toLocaleString()} M USD</span>
      </div>
    </div>
  )
}
