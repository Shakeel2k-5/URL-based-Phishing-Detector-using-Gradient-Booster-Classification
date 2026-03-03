import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';

export default function ResultCard({ result }) {
  if (!result) return null;

  return (
    <Card className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm text-gray-500 mb-1">Analyzed URL</p>
          <p className="text-gray-900 font-medium truncate" title={result.url}>
            {result.url}
          </p>
        </div>
        <StatusBadge safe={result.safe} />
      </div>
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className={`text-sm ${result.safe ? 'text-emerald-600' : 'text-red-600'}`}>
          {result.safe
            ? 'This URL appears to be legitimate and safe to visit.'
            : 'Warning: This URL has been identified as potentially dangerous. Avoid visiting it.'}
        </p>
      </div>
    </Card>
  );
}
