import { useGeos } from '../hooks/useGeos'

export default function MinistryRanking() {
  const { data: ranking } = useGeos<{ name: string; governance_score: number }[]>('/ministries/ranking')

  if (!ranking?.length) return null

  const max = Math.max(...ranking.map((m) => m.governance_score))

  return (
    <div>
      {ranking.map((m, i) => (
        <div key={m.name} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
          <span style={{ width: 20, color: '#94a3b8', fontSize: 12 }}>#{i + 1}</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 14, marginBottom: 4 }}>{m.name}</div>
            <div style={{ height: 8, background: '#1e293b', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${(m.governance_score / max) * 100}%`,
                background: m.governance_score > 40 ? '#10b981' : '#f59e0b',
                borderRadius: 4,
                transition: 'width 0.5s',
              }} />
            </div>
          </div>
          <span style={{ fontSize: 14, fontWeight: 600, width: 50, textAlign: 'right' }}>
            {m.governance_score}
          </span>
        </div>
      ))}
    </div>
  )
}
