import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface Props {
  snn: {
    positive: { cs: number; ps: number; gr: number; nrv: number }
    costs: { dwl: number; ec: number }
  }
}

export default function SnDonut({ snn }: Props) {
  const data = {
    labels: ['CS', 'PS', 'GR', 'NRV', 'DWL', 'EC'],
    datasets: [{
      data: [
        snn.positive.cs,
        snn.positive.ps,
        snn.positive.gr,
        snn.positive.nrv,
        snn.costs.dwl,
        snn.costs.ec,
      ],
      backgroundColor: [
        '#3b82f6', '#10b981', '#8b5cf6', '#06b6d4',
        '#ef4444', '#f59e0b',
      ],
      borderWidth: 0,
      hoverOffset: 8,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: { color: '#94a3b8', padding: 16, font: { size: 12 } },
      },
    },
  }

  return (
    <div style={{ height: 280 }}>
      <Doughnut data={data} options={options} />
    </div>
  )
}
