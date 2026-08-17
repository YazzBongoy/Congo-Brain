import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

interface Props {
  snn: {
    positive: { cs: number; ps: number; gr: number; nrv: number; total: number }
    costs: { dwl: number; ec: number; total: number }
  }
}

export default function SnnBar({ snn }: Props) {
  const data = {
    labels: ['CS', 'PS', 'GR', 'NRV', 'DWL', 'EC'],
    datasets: [{
      label: 'M USD',
      data: [
        snn.positive.cs,
        snn.positive.ps,
        snn.positive.gr,
        snn.positive.nrv,
        -snn.costs.dwl,
        -snn.costs.ec,
      ],
      backgroundColor: [
        '#3b82f6', '#10b981', '#8b5cf6', '#06b6d4',
        '#ef4444', '#f59e0b',
      ],
      borderRadius: 6,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        grid: { color: '#1e293b' },
        ticks: { color: '#94a3b8' },
      },
      y: {
        grid: { color: '#1e293b' },
        ticks: { color: '#94a3b8', callback: (v: number) => `${v} M` },
      },
    },
  }

  return (
    <div style={{ height: 280 }}>
      <Bar data={data} options={options} />
    </div>
  )
}
