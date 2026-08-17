import { useGeos } from '../hooks/useGeos'

interface Company {
  name: string
  sector: string
  revenue: number
  production_cost: number
  tax_burden: number
  admin_cost: number
  corruption_cost: number
  logistics_cost: number
  energy_cost: number
  employees: number
}

export default function Companies() {
  const { data: companies, loading } = useGeos<Company[]>('/companies')
  const { data: psData } = useGeos<{ total_ps: number; details: Record<string, number> }>('/companies/ps/total')

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!companies) return null

  return (
    <>
      <div className="page-header">
        <h2>Entreprises</h2>
        <p>Surplus des producteurs et coûts opérationnels</p>
      </div>

      {psData && (
        <div className="cards-grid">
          <div className="card">
            <div className="card-label">PS Total</div>
            <div className="card-value positive">{psData.total_ps.toLocaleString()} M USD</div>
          </div>
        </div>
      )}

      <div className="table-card">
        <h3>Entreprises</h3>
        <table>
          <thead>
            <tr>
              <th>Entreprise</th>
              <th>Secteur</th>
              <th>Revenus</th>
              <th>Coûts totaux</th>
              <th>PS</th>
              <th>Corruption</th>
              <th>Employés</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((c) => {
              const totalCost = c.production_cost + c.tax_burden + c.admin_cost
                + c.corruption_cost + c.logistics_cost + c.energy_cost
              const ps = Math.max(0, c.revenue - totalCost)
              return (
                <tr key={c.name}>
                  <td><strong>{c.name}</strong></td>
                  <td><span className="badge badge-blue">{c.sector}</span></td>
                  <td>{c.revenue.toLocaleString()} M</td>
                  <td>{totalCost.toLocaleString()} M</td>
                  <td style={{ color: '#10b981', fontWeight: 600 }}>{ps.toLocaleString()} M</td>
                  <td style={{ color: '#ef4444' }}>{c.corruption_cost} M</td>
                  <td>{c.employees.toLocaleString()}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </>
  )
}
