import { SectorProgress as SectorProgressData } from '../dashboardModel'

interface Props {
  sectors: SectorProgressData[]
}

export default function SectorProgress({ sectors }: Props) {
  return (
    <section className="dashboard-panel" aria-labelledby="sector-progress-title">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Portefeuille sectoriel</span>
          <h3 id="sector-progress-title">Achèvement par secteur</h3>
        </div>
        <span className="method-note" title="Pondéré par le coût: terminé 100%, en cours 50%, planifié 0%">
          Estimation par statut ⓘ
        </span>
      </div>

      <div className="sector-grid">
        {sectors.map((sector) => (
          <article className="sector-item" key={sector.sector}>
            <div className="sector-topline">
              <div>
                <strong>{sector.sector}</strong>
                <span>{sector.portfolioBudget.toLocaleString()} M USD · {sector.projectCount} projet{sector.projectCount > 1 ? 's' : ''}</span>
              </div>
              <b>{sector.progressRate}%</b>
            </div>
            <div className="progress-track sector-progress-track">
              <div className="progress-fill progress-primary" style={{ width: `${sector.progressRate}%` }} />
            </div>
            <div className="sector-statuses">
              <span className="completed-dot">{sector.completed} terminé</span>
              <span className="ongoing-dot">{sector.ongoing} en cours</span>
              <span className="planned-dot">{sector.planned} planifié</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
