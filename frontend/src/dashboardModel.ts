export interface MinistryBudget {
  name: string
  budget_allocated: number
  budget_executed: number
  optimization_score: number
  transparency_score: number
  performance_score: number
  satisfaction_score: number
}

export interface PublicProject {
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

export interface ProjectAllocation {
  fraction: number
  snn: number
}

export interface MinistryExecution extends MinistryBudget {
  executionRate: number
  remaining: number
}

export interface SectorProgress {
  sector: string
  portfolioBudget: number
  progressRate: number
  completed: number
  ongoing: number
  planned: number
  projectCount: number
}

const STATUS_PROGRESS: Record<string, number> = {
  completed: 100,
  ongoing: 50,
  awarded: 20,
  planned: 0,
}

export function getMinistryExecution(ministries: MinistryBudget[]): MinistryExecution[] {
  return ministries
    .map((ministry) => ({
      ...ministry,
      executionRate: ministry.budget_allocated > 0
        ? Math.min(100, Math.round((ministry.budget_executed / ministry.budget_allocated) * 100))
        : 0,
      remaining: Math.max(0, ministry.budget_allocated - ministry.budget_executed),
    }))
    .sort((a, b) => b.budget_allocated - a.budget_allocated)
}

export function getSectorProgress(projects: PublicProject[]): SectorProgress[] {
  const sectors = new Map<string, {
    budget: number
    weightedProgress: number
    completed: number
    ongoing: number
    planned: number
    count: number
  }>()

  projects.forEach((project) => {
    const current = sectors.get(project.sector) ?? {
      budget: 0,
      weightedProgress: 0,
      completed: 0,
      ongoing: 0,
      planned: 0,
      count: 0,
    }
    const progress = STATUS_PROGRESS[project.status] ?? 0
    current.budget += project.cost
    current.weightedProgress += project.cost * progress
    current.count += 1
    if (project.status === 'completed') current.completed += 1
    else if (project.status === 'ongoing') current.ongoing += 1
    else current.planned += 1
    sectors.set(project.sector, current)
  })

  return Array.from(sectors.entries())
    .map(([sector, values]) => ({
      sector,
      portfolioBudget: values.budget,
      progressRate: values.budget > 0 ? Math.round(values.weightedProgress / values.budget) : 0,
      completed: values.completed,
      ongoing: values.ongoing,
      planned: values.planned,
      projectCount: values.count,
    }))
    .sort((a, b) => b.portfolioBudget - a.portfolioBudget)
}

export function getProjectSnn(project: PublicProject): number {
  return project.cs_impact + project.ps_impact + project.gr_impact
    + project.nrv_impact - project.dwl_impact - project.ec_impact
}

export function formatStatus(status: string): string {
  const labels: Record<string, string> = {
    completed: 'Terminé',
    ongoing: 'En cours',
    awarded: 'Attribué',
    planned: 'Planifié',
  }
  return labels[status] ?? status
}
