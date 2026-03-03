import { useState } from 'react';
import StatusBadge from '../common/StatusBadge';
import Card from '../common/Card';

const PER_PAGE = 15;

export default function HistoryTable({ checks, onDelete }) {
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(checks.length / PER_PAGE);
  const displayed = checks.slice(page * PER_PAGE, (page + 1) * PER_PAGE);

  if (checks.length === 0) {
    return (
      <Card>
        <p className="text-sm text-gray-500 text-center py-8">No matching results.</p>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden !p-0">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left font-medium text-gray-500 px-6 py-3">URL</th>
              <th className="text-left font-medium text-gray-500 px-6 py-3">Result</th>
              <th className="text-left font-medium text-gray-500 px-6 py-3">Feedback</th>
              <th className="text-left font-medium text-gray-500 px-6 py-3">Date</th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {displayed.map((check) => (
              <tr key={check.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="px-6 py-3 max-w-sm truncate text-gray-700" title={check.url}>
                  {check.url}
                </td>
                <td className="px-6 py-3">
                  <StatusBadge safe={check.safe} />
                </td>
                <td className="px-6 py-3 text-gray-500">
                  {check.feedbackGiven ? (
                    <span className="text-indigo-600 font-medium">
                      Reported as {check.feedbackGiven === 'safe' ? 'Safe' : 'Phishing'}
                    </span>
                  ) : (
                    <span className="text-gray-400">None</span>
                  )}
                </td>
                <td className="px-6 py-3 text-gray-500 whitespace-nowrap">
                  {new Date(check.checkedAt).toLocaleDateString()}{' '}
                  {new Date(check.checkedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </td>
                <td className="px-6 py-3">
                  <button
                    onClick={() => onDelete(check.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-6 py-3 border-t border-gray-200 bg-gray-50">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </Card>
  );
}
