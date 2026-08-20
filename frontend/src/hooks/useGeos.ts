import { useState, useEffect } from 'react'
import axios from 'axios'

const API = '/api/v1/geos'

export function useGeos<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    axios.get(`${API}${path}`)
      .then((r) => { setData(r.data); setError(null) })
      .catch((e) => { setError(e.message) })
      .finally(() => { setLoading(false) })
  }, [path])

  return { data, loading, error }
}

export function useDashboard() {
  return useGeos<{
    snn: {
      snn: number
      snn_rate: number
      positive: { cs: number; ps: number; gr: number; nrv: number; total: number }
      costs: { dwl: number; ec: number; total: number }
      sources: Record<string, Record<string, number>>
    }
    optimization: {
      budget: number
      total_snn: number
      remaining: number
      allocations: Record<string, { fraction: number; snn: number }>
    }
    entity_counts: Record<string, number>
  }>('/dashboard')
}

export function useSnn() {
  return useGeos<{
    snn: number
    snn_rate: number
    positive: { cs: number; ps: number; gr: number; nrv: number; total: number }
    costs: { dwl: number; ec: number; total: number }
  }>('/snn')
}
