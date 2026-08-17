import { useDashboard } from '../hooks/useGeos'
import SnDonut from '../components/SnDonut'
import SnnBar from '../components/SnnBar'
import ProvinceTable from '../components/ProvinceTable'
import MinistryRanking from '../components/MinistryRanking'
import ResourceBreakdown from '../components/ResourceBreakdown'
import OptimizationCard from '../components/OptimizationCard'

export default function Dashboard() {
  const { data, loading, error } = useDashboard()

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (error || !data) return <div className="loading">Erreur: {error}</div>

  const { snn, optimization, entity_counts } = data
  const net = snn.snn

  return (
    <>
      <div className="formula-banner">
        <h2>max SNN = CS + PS + GR + NRV − DWL − EC</h2>
        <p>Government Economic Optimization System — Surplus National Net</p>
      </div>

      <div className="cards-grid">
        <div className="card">
          <div className="card-label">SNN Total</div>
          <div className={`card-value ${net >= 0 ? 'positive' : 'negative'}`}>
            {net.toLocaleString()} M USD
          </div>
          <div className="card-sub">Taux: {snn.snn_rate}%</div>
        </div>
        <div className="card">
          <div className="card-label">Consumer Surplus</div>
          <div className="card-value neutral">{snn.positive.cs.toLocaleString()} M</div>
          <div className="card-sub">Services publics</div>
        </div>
        <div className="card">
          <div className="card-label">Producer Surplus</div>
          <div className="card-value neutral">{snn.positive.ps.toLocaleString()} M</div>
          <div className="card-sub">Entreprises</div>
        </div>
        <div className="card">
          <div className="card-label">Government Revenue</div>
          <div className="card-value neutral">{snn.positive.gr.toLocaleString()} M</div>
          <div className="card-sub">Impôts & douanes</div>
        </div>
        <div className="card">
          <div className="card-label">NRV</div>
          <div className="card-value neutral">{snn.positive.nrv.toLocaleString()} M</div>
          <div className="card-sub">Ressources naturelles</div>
        </div>
        <div className="card">
          <div className="card-label">DWL</div>
          <div className="card-value negative">−{snn.costs.dwl.toLocaleString()} M</div>
          <div className="card-sub">Corruption & évasion</div>
        </div>
        <div className="card">
          <div className="card-label">EC</div>
          <div className="card-value negative">−{snn.costs.ec.toLocaleString()} M</div>
          <div className="card-sub">Coûts environnementaux</div>
        </div>
        <div className="card">
          <div className="card-label">Entités</div>
          <div className="card-value neutral">
            {Object.values(entity_counts).reduce((a, b) => a + b, 0)}
          </div>
          <div className="card-sub">14 tables GEOS</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <h3>Répartition du SNN</h3>
          <SnDonut snn={snn} />
        </div>
        <div className="chart-card">
          <h3>Composantes du SNN</h3>
          <SnnBar snn={snn} />
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <h3>Classement Ministères</h3>
          <MinistryRanking />
        </div>
        <div className="chart-card">
          <h3>Ressources par Minéral</h3>
          <ResourceBreakdown />
        </div>
      </div>

      <OptimizationCard optimization={optimization} />
      <ProvinceTable />
    </>
  )
}
