import { useGeos } from '../hooks/useGeos'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

interface Province {
  name: string
  population: number
  gdp: number
  poverty_rate: number
  literacy_rate: number
  electricity_access: number
  water_access: number
  governance_score: number
}

export default function Provinces() {
  const { data: provinces, loading } = useGeos<Province[]>('/provinces')

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!provinces) return null

  const chartData = {
    labels: provinces.map((p) => p.name),
    datasets: [
      {
        label: 'PIB (M USD)',
        data: provinces.map((p) => p.gdp),
        backgroundColor: '#3b82f6',
        borderRadius: 6,
      },
      {
        label: 'Population (M)',
        data: provinces.map((p) => p.population * 1000),
        backgroundColor: '#8b5cf6',
        borderRadius: 6,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#94a3b8' } } },
    scales: {
      x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
      y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
    },
  }

  return (
    <>
      <div className="page-header">
        <h2>Provinces</h2>
        <p>Indicateurs socio-économiques par province</p>
      </div>

      <div className="chart-card" style={{ marginBottom: 24 }}>
        <h3>PIB et Population par Province</h3>
        <div style={{ height: 300 }}>
          <Bar data={chartData} options={chartOptions} />
        </div>
      </div>

      <div className="table-card">
        <h3>Détail des Provinces</h3>
        <table>
          <thead>
            <tr>
              <th>Province</th>
              <th>Population</th>
              <th>PIB</th>
              <th>Pauvreté</th>
              <th>Éducation</th>
              <th>Électricité</th>
              <th>Eau</th>
              <th>Gouvernance</th>
            </tr>
          </thead>
          <tbody>
            {provinces.map((p) => (
              <tr key={p.name}>
                <td><strong>{p.name}</strong></td>
                <td>{p.population} M</td>
                <td>{p.gdp.toLocaleString()} M</td>
                <td><span className={`badge ${p.poverty_rate > 60 ? 'badge-red' : 'badge-yellow'}`}>{p.poverty_rate}%</span></td>
                <td>{p.literacy_rate}%</td>
                <td><span className={`badge ${p.electricity_access > 30 ? 'badge-green' : 'badge-red'}`}>{p.electricity_access}%</span></td>
                <td><span className={`badge ${p.water_access > 40 ? 'badge-green' : 'badge-yellow'}`}>{p.water_access}%</span></td>
                <td><span className={`badge ${p.governance_score > 40 ? 'badge-green' : 'badge-yellow'}`}>{p.governance_score}/100</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
