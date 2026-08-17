import { useGeos } from '../hooks/useGeos'

export default function ProvinceTable() {
  const { data: provinces } = useGeos<{ name: string; population: number; gdp: number; poverty_rate: number; governance_score: number }[]>('/provinces')

  if (!provinces?.length) return null

  return (
    <div className="table-card">
      <h3>Provinces</h3>
      <table>
        <thead>
          <tr>
            <th>Province</th>
            <th>Population (M)</th>
            <th>PIB (M USD)</th>
            <th>Pauvreté</th>
            <th>Gouvernance</th>
          </tr>
        </thead>
        <tbody>
          {provinces.map((p) => (
            <tr key={p.name}>
              <td><strong>{p.name}</strong></td>
              <td>{p.population}</td>
              <td>{p.gdp.toLocaleString()}</td>
              <td>
                <span className={`badge ${p.poverty_rate > 60 ? 'badge-red' : p.poverty_rate > 40 ? 'badge-yellow' : 'badge-green'}`}>
                  {p.poverty_rate}%
                </span>
              </td>
              <td>
                <span className={`badge ${p.governance_score > 45 ? 'badge-green' : 'badge-yellow'}`}>
                  {p.governance_score}/100
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
