import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useHistory } from '../../hooks/useHistory';
import Card from '../common/Card';

const COLORS = ['#10b981', '#ef4444'];

export default function SafetyPieChart() {
  const { getStats } = useHistory();
  const stats = getStats();

  if (stats.total === 0) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Safety Distribution</h3>
        <p className="text-sm text-gray-500 text-center py-8">No data to display yet.</p>
      </Card>
    );
  }

  const data = [
    { name: 'Safe', value: stats.safe },
    { name: 'Phishing', value: stats.phishing },
  ];

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Safety Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={4}
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}
