import { useGeos } from '../hooks/useGeos'

interface Ministry {
  name: string
  budget_allocated: number
  budget_executed: number
  optimization_score: number
  transparency_score: number
  performance_score: number
  satisfaction_score: number
}

export default function Ministries() {
  const { data: ministries, loading } = useGeos<Ministry[]>('/ministries')

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!ministries) return null

  return (
    <>
      <div className="page-header">
        <h2>Ministères</h2>
        <p>Scores de gouvernance et exécution budgétaire</p>
      </div>

      <div className="cards-grid">
        {ministries.map((m) => {
          const gs = (0.4 * m.optimization_score + 0.2 * m.transparency_score
            + 0.2 * m.performance_score + 0.2 * m.satisfaction_score)
          const execRate = m.budget_allocated > 0
            ? Math.round(m.budget_executed / m.budget_allocated * 100)
            : 0

          return (
            <div key={m.name} className="card">
              <div className="card-label">{m.name}</div>
              <div className="card-value neutral" style={{ fontSize: 24 }}>
                {gs.toFixed(1)}<span style={{ fontSize: 12, color: '#94a3b8' }}>/100</span>
              </div>
              <div className="card-sub">
                Exécution: <span className={`badge ${execRate > 70 ? 'badge-green' : 'badge-yellow'}`}>{execRate}%</span>
              </div>
              <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 11, color: '#94a3b8' }}>
                <div>Opt: {m.optimization_score}</div>
                <div>Trans: {m.transparency_score}</div>
                <div>Perf: {m.performance_score}</div>
                <div>Sat: {m.satisfaction_score}</div>
              </div>
            </div>
          )
        })}
      </div>
    </>
  )
}
