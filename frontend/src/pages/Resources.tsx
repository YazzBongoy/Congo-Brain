import { useGeos } from '../hooks/useGeos'

interface Resource {
  name: string
  mineral_type: string
  annual_production_tons: number
  market_value_per_ton: number
  local_processing_pct: number
  tax_rate: number
  environmental_cost: number
}

export default function Resources() {
  const { data: resources, loading } = useGeos<Resource[]>('/resources')
  const { data: nrvData } = useGeos<{ total_nrv: number; details: Record<string, number> }>('/resources/nrv/total')

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!resources) return null

  return (
    <>
      <div className="page-header">
        <h2>Ressources Naturelles</h2>
        <p>Mines et valeur des ressources de la RDC</p>
      </div>

      {nrvData && (
        <div className="cards-grid">
          <div className="card">
            <div className="card-label">NRV Total</div>
            <div className="card-value neutral">{nrvData.total_nrv.toLocaleString()} M USD</div>
          </div>
        </div>
      )}

      <div className="table-card">
        <h3>Mines</h3>
        <table>
          <thead>
            <tr>
              <th>Mine</th>
              <th>Minéral</th>
              <th>Production (t/an)</th>
              <th>Valeur/t</th>
              <th>Transformation</th>
              <th>Taxe</th>
              <th>EC</th>
              <th>NRV</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((r) => {
              const nrv = r.annual_production_tons * r.market_value_per_ton / 1_000_000 * (1 + r.local_processing_pct / 100)
              return (
                <tr key={r.name}>
                  <td><strong>{r.name}</strong></td>
                  <td><span className="badge badge-blue">{r.mineral_type}</span></td>
                  <td>{r.annual_production_tons.toLocaleString()}</td>
                  <td>${r.market_value_per_ton.toLocaleString()}</td>
                  <td><span className={`badge ${r.local_processing_pct > 10 ? 'badge-green' : 'badge-yellow'}`}>{r.local_processing_pct}%</span></td>
                  <td>{r.tax_rate}%</td>
                  <td style={{ color: '#ef4444' }}>{r.environmental_cost} M</td>
                  <td style={{ color: '#10b981', fontWeight: 600 }}>{nrv.toFixed(1)} M</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </>
  )
}
