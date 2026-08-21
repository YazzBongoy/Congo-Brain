interface Props {
  optimization: {
    budget: number
    total_snn: number
    allocations: Record<string, { fraction: number; snn: number }>
  }
}

export default function OptimizationCard({ optimization }: Props) {
  const entries = Object.entries(optimization.allocations)
    .sort((a, b) => b[1].snn - a[1].snn)

  return (
    <div className="table-card">
      <h3>Allocation Optimale — Budget {optimization.budget.toLocaleString()} M USD</h3>
      <table>
        <thead>
          <tr>
            <th>Projet</th>
            <th>Allocation</th>
            <th>Impact SNN</th>
            <th>Efficacité</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([name, alloc]) => (
            <tr key={name}>
              <td><strong>{name}</strong></td>
              <td>
                <span className="badge badge-blue">
                  {(alloc.fraction * 100).toFixed(0)}%
                </span>
              </td>
              <td style={{ color: alloc.snn > 0 ? '#10b981' : '#ef4444' }}>
                {alloc.snn > 0 ? '+' : ''}{alloc.snn.toFixed(1)} M
              </td>
              <td>
                <div style={{ height: 6, background: '#1e293b', borderRadius: 3, width: 100 }}>
                  <div style={{
                    height: '100%',
                    width: `${Math.min(100, alloc.snn / optimization.total_snn * 100)}%`,
                    background: '#10b981',
                    borderRadius: 3,
                  }} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={2} style={{ fontWeight: 600 }}>SNN Total</td>
            <td colSpan={2} style={{ fontWeight: 700, color: '#10b981', fontSize: 16 }}>
              +{optimization.total_snn.toLocaleString()} M USD
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
