import { useNavigate } from 'react-router-dom';
import StatsGrid from '../components/dashboard/StatsGrid';
import RecentChecksTable from '../components/dashboard/RecentChecksTable';
import SafetyPieChart from '../components/dashboard/SafetyPieChart';
import UrlInput from '../components/url-checker/UrlInput';
import Card from '../components/common/Card';
import { predictUrl } from '../api/client';
import { useHistory } from '../hooks/useHistory';
import { useApi } from '../hooks/useApi';
import ErrorAlert from '../components/common/ErrorAlert';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { addCheck } = useHistory();
  const { loading, error, execute, clearError } = useApi();

  const handleCheck = async (url) => {
    try {
      const result = await execute(() => predictUrl(url));
      addCheck(result);
      navigate('/check', { state: { result } });
    } catch {
      // error handled by useApi
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h1>
        <p className="text-gray-500">Overview of your phishing detection activity</p>
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Check</h3>
        <UrlInput onSubmit={handleCheck} loading={loading} />
        {error && <div className="mt-4"><ErrorAlert message={error} onDismiss={clearError} /></div>}
      </Card>

      <StatsGrid />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentChecksTable />
        </div>
        <div>
          <SafetyPieChart />
        </div>
      </div>
    </div>
  );
}
