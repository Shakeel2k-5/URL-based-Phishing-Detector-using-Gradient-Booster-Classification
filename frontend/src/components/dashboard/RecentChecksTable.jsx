import { useHistory } from '../../hooks/useHistory';
import StatusBadge from '../common/StatusBadge';
import Card from '../common/Card';

function timeAgo(dateStr) {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function RecentChecksTable() {
  const { checks } = useHistory();
  const recent = checks.slice(0, 10);

  if (recent.length === 0) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Checks</h3>
        <p className="text-sm text-gray-500 text-center py-8">
          No URLs checked yet. Go to Check URL to get started.
        </p>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden !p-0">
      <h3 className="text-lg font-semibold text-gray-900 p-6 pb-0">Recent Checks</h3>
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-t border-b border-gray-100">
              <th className="text-left font-medium text-gray-500 px-6 py-3">URL</th>
              <th className="text-left font-medium text-gray-500 px-6 py-3">Result</th>
              <th className="text-right font-medium text-gray-500 px-6 py-3">Time</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((check) => (
              <tr key={check.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="px-6 py-3 max-w-xs truncate text-gray-700" title={check.url}>
                  {check.url}
                </td>
                <td className="px-6 py-3">
                  <StatusBadge safe={check.safe} />
                </td>
                <td className="px-6 py-3 text-right text-gray-500 whitespace-nowrap">
                  {timeAgo(check.checkedAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
