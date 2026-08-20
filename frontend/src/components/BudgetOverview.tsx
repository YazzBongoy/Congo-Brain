import { MinistryExecution } from '../dashboardModel'

interface Props {
  ministries: MinistryExecution[]
}

function executionTone(rate: number) {
  if (rate >= 75) return 'progress-success'
  if (rate >= 50) return 'progress-warning'
  return 'progress-danger'
}

export default function BudgetOverview({ ministries }: Props) {
  return (
    <section className="dashboard-panel dashboard-panel-wide" aria-labelledby="budget-title">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Exécution budgétaire</span>
          <h3 id="budget-title">Budgets par ministère</h3>
        </div>
        <div className="panel-legend">
          <span><i className="legend-dot allocated" /> Alloué</span>
          <span><i className="legend-dot executed" /> Exécuté</span>
        </div>
      </div>

      <div className="responsive-table">
        <table className="budget-table">
          <thead>
            <tr>
              <th>Ministère</th>
              <th>Budget alloué</th>
              <th>Exécuté</th>
              <th>Solde</th>
              <th>Achèvement</th>
            </tr>
          </thead>
          <tbody>
            {ministries.map((ministry) => (
              <tr key={ministry.name}>
                <td>
                  <strong>{ministry.name}</strong>
                  <span className="table-secondary">Score d'optimisation {ministry.optimization_score}/100</span>
                </td>
                <td className="numeric">{ministry.budget_allocated.toLocaleString()} M USD</td>
                <td className="numeric executed-value">{ministry.budget_executed.toLocaleString()} M USD</td>
                <td className="numeric">{ministry.remaining.toLocaleString()} M USD</td>
                <td>
                  <div className="progress-cell">
                    <div className="progress-track" aria-label={`${ministry.executionRate}% exécuté`}>
                      <div
                        className={`progress-fill ${executionTone(ministry.executionRate)}`}
                        style={{ width: `${ministry.executionRate}%` }}
                      />
                    </div>
                    <strong>{ministry.executionRate}%</strong>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
