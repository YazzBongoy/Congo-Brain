import BudgetOverview from '../components/BudgetOverview'
import OptimizedProjects from '../components/OptimizedProjects'
import SectorProgress from '../components/SectorProgress'
import SnDonut from '../components/SnDonut'
import SnnBar from '../components/SnnBar'
import {
  getMinistryExecution,
  getSectorProgress,
  MinistryBudget,
  PublicProject,
} from '../dashboardModel'
import { useDashboard, useGeos } from '../hooks/useGeos'

export default function Dashboard() {
  const dashboard = useDashboard()
  const ministriesRequest = useGeos<MinistryBudget[]>('/ministries')
  const projectsRequest = useGeos<PublicProject[]>('/projects')

  if (dashboard.loading || ministriesRequest.loading || projectsRequest.loading) {
    return <div className="loading"><div className="spinner" /><span>Chargement du pilotage budgétaire…</span></div>
  }

  const error = dashboard.error || ministriesRequest.error || projectsRequest.error
  if (error || !dashboard.data || !ministriesRequest.data || !projectsRequest.data) {
    return <div className="loading error-state">Impossible de charger le dashboard : {error ?? 'données indisponibles'}</div>
  }

  const { snn, optimization } = dashboard.data
  const ministries = getMinistryExecution(ministriesRequest.data)
  const sectors = getSectorProgress(projectsRequest.data)
  const totalAllocated = ministries.reduce((sum, item) => sum + item.budget_allocated, 0)
  const totalExecuted = ministries.reduce((sum, item) => sum + item.budget_executed, 0)
  const nationalExecution = totalAllocated > 0 ? Math.round((totalExecuted / totalAllocated) * 100) : 0
  const optimizedProjectCount = Object.keys(optimization.allocations).length
  const committedBudget = optimization.budget - optimization.remaining

  return (
    <div className="executive-dashboard">
      <header className="executive-header">
        <div>
          <span className="eyebrow">GEOS · Vue exécutive</span>
          <h2>Pilotage budgétaire national</h2>
          <p>Budgets ministériels, exécution sectorielle et portefeuille de projets optimisés.</p>
        </div>
        <div className="data-quality-tag">
          <span className="live-dot" /> Données de référence GEOS
        </div>
      </header>

      <section className="executive-kpis" aria-label="Indicateurs budgétaires principaux">
        <article className="kpi-tile kpi-primary">
          <span>Budget ministériel</span>
          <strong>{totalAllocated.toLocaleString()} <small>M USD</small></strong>
          <p>{ministries.length} ministères suivis</p>
        </article>
        <article className="kpi-tile">
          <span>Budget exécuté</span>
          <strong>{totalExecuted.toLocaleString()} <small>M USD</small></strong>
          <div className="kpi-progress"><i style={{ width: `${nationalExecution}%` }} /></div>
          <p>{nationalExecution}% d'exécution nationale</p>
        </article>
        <article className="kpi-tile">
          <span>Budget optimisé engagé</span>
          <strong>{committedBudget.toLocaleString()} <small>M USD</small></strong>
          <p>sur {optimization.budget.toLocaleString()} M USD disponibles</p>
        </article>
        <article className="kpi-tile">
          <span>Projets optimisés</span>
          <strong>{optimizedProjectCount}</strong>
          <p>Impact SNN +{optimization.total_snn.toLocaleString()} M USD</p>
        </article>
        <article className="kpi-tile">
          <span>Surplus national net</span>
          <strong className={snn.snn >= 0 ? 'positive' : 'negative'}>{snn.snn.toLocaleString()} <small>M USD</small></strong>
          <p>Taux de valeur nette {snn.snn_rate}%</p>
        </article>
      </section>

      <BudgetOverview ministries={ministries} />

      <div className="dashboard-two-column">
        <OptimizedProjects projects={projectsRequest.data} allocations={optimization.allocations} />
        <SectorProgress sectors={sectors} />
      </div>

      <section className="dashboard-panel dashboard-panel-wide economic-panel" aria-labelledby="snn-analysis-title">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Analyse économique</span>
            <h3 id="snn-analysis-title">Composition du surplus national net</h3>
          </div>
          <span className="formula-chip">SNN = CS + PS + GR + NRV − DWL − EC</span>
        </div>
        <div className="embedded-chart-grid">
          <div>
            <h4>Répartition</h4>
            <SnDonut snn={snn} />
          </div>
          <div>
            <h4>Composantes</h4>
            <SnnBar snn={snn} />
          </div>
        </div>
      </section>
    </div>
  )
}
