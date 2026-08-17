import { useGeos } from '../hooks/useGeos'

interface Project {
  name: string
  sector: string
  cost: number
  cs_impact: number
  ps_impact: number
  gr_impact: number
  nrv_impact: number
  dwl_impact: number
  ec_impact: number
  status: string
}

export default function Projects() {
  const { data: projects, loading } = useGeos<Project[]>('/projects')
  const { data: snnData } = useGeos<{ total_snn: number; details: Record<string, number> }>('/projects/snn/total')

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!projects) return null

  return (
    <>
      <div className="page-header">
        <h2>Projets</h2>
        <p>Impact SNN des projets publics</p>
      </div>

      {snnData && (
        <div className="cards-grid">
          <div className="card">
            <div className="card-label">SNN Total Projets</div>
            <div className="card-value positive">+{snnData.total_snn.toLocaleString()} M USD</div>
          </div>
        </div>
      )}

      <div className="table-card">
        <h3>Projets</h3>
        <table>
          <thead>
            <tr>
              <th>Projet</th>
              <th>Secteur</th>
              <th>Coût</th>
              <th>CS</th>
              <th>PS</th>
              <th>GR</th>
              <th>NRV</th>
              <th>DWL</th>
              <th>EC</th>
              <th>SNN</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => {
              const snn = p.cs_impact + p.ps_impact + p.gr_impact + p.nrv_impact - p.dwl_impact - p.ec_impact
              return (
                <tr key={p.name}>
                  <td><strong>{p.name}</strong></td>
                  <td><span className="badge badge-blue">{p.sector}</span></td>
                  <td>{p.cost.toLocaleString()} M</td>
                  <td style={{ color: '#3b82f6' }}>+{p.cs_impact}</td>
                  <td style={{ color: '#10b981' }}>+{p.ps_impact}</td>
                  <td style={{ color: '#8b5cf6' }}>+{p.gr_impact}</td>
                  <td style={{ color: '#06b6d4' }}>+{p.nrv_impact}</td>
                  <td style={{ color: '#ef4444' }}>-{p.dwl_impact}</td>
                  <td style={{ color: '#f59e0b' }}>-{p.ec_impact}</td>
                  <td style={{ color: snn > 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                    {snn > 0 ? '+' : ''}{snn.toFixed(1)} M
                  </td>
                  <td>
                    <span className={`badge ${p.status === 'completed' ? 'badge-green' : p.status === 'ongoing' ? 'badge-blue' : 'badge-yellow'}`}>
                      {p.status}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </>
  )
}
