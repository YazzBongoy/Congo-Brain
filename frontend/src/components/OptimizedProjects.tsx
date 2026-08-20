import { formatStatus, getProjectSnn, ProjectAllocation, PublicProject } from '../dashboardModel'

interface Props {
  projects: PublicProject[]
  allocations: Record<string, ProjectAllocation>
}

const statusClass: Record<string, string> = {
  completed: 'status-completed',
  ongoing: 'status-ongoing',
  awarded: 'status-awarded',
  planned: 'status-planned',
}

export default function OptimizedProjects({ projects, allocations }: Props) {
  const optimized = Object.entries(allocations)
    .map(([name, allocation]) => ({
      project: projects.find((item) => item.name === name),
      allocation,
    }))
    .filter((item): item is { project: PublicProject; allocation: ProjectAllocation } => Boolean(item.project))
    .sort((a, b) => b.allocation.snn - a.allocation.snn)

  return (
    <section className="dashboard-panel" aria-labelledby="optimized-projects-title">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Portefeuille prioritaire</span>
          <h3 id="optimized-projects-title">Projets optimisés</h3>
        </div>
        <span className="panel-count">{optimized.length} sélectionnés</span>
      </div>

      <div className="optimized-list">
        {optimized.map(({ project, allocation }, index) => (
          <article className="optimized-project" key={project.name}>
            <span className="project-rank">{String(index + 1).padStart(2, '0')}</span>
            <div className="project-main">
              <div className="project-title-row">
                <strong>{project.name}</strong>
                <span className={`status-pill ${statusClass[project.status] ?? 'status-planned'}`}>
                  {formatStatus(project.status)}
                </span>
              </div>
              <div className="project-meta">
                <span>{project.sector}</span>
                <span>{project.cost.toLocaleString()} M USD</span>
                <span>SNN potentiel +{getProjectSnn(project).toFixed(1)} M</span>
              </div>
              <div className="funding-row">
                <div className="progress-track">
                  <div className="progress-fill progress-primary" style={{ width: `${allocation.fraction * 100}%` }} />
                </div>
                <strong>{Math.round(allocation.fraction * 100)}% financé</strong>
              </div>
            </div>
            <div className="project-impact">
              <span>Impact optimisé</span>
              <strong>+{allocation.snn.toFixed(1)} M</strong>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
