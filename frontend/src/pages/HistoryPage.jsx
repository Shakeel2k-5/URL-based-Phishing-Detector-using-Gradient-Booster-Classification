import { useState, useMemo } from 'react';
import { useHistory } from '../hooks/useHistory';
import HistoryFilters from '../components/history/HistoryFilters';
import HistoryTable from '../components/history/HistoryTable';
import ConfirmModal from '../components/common/ConfirmModal';

export default function HistoryPage() {
  const { checks, deleteCheck, clearHistory } = useHistory();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const filtered = useMemo(() => {
    return checks.filter((check) => {
      const matchesSearch = check.url.toLowerCase().includes(search.toLowerCase());
      const matchesFilter =
        filter === 'all' ||
        (filter === 'safe' && check.safe) ||
        (filter === 'phishing' && !check.safe);
      return matchesSearch && matchesFilter;
    });
  }, [checks, search, filter]);

  const handleClear = () => {
    clearHistory();
    setShowClearConfirm(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Check History</h1>
        <p className="text-gray-500">View and manage all previously checked URLs</p>
      </div>

      <HistoryFilters
        search={search}
        onSearchChange={setSearch}
        filter={filter}
        onFilterChange={setFilter}
        onClear={() => setShowClearConfirm(true)}
        total={filtered.length}
      />

      <HistoryTable checks={filtered} onDelete={deleteCheck} />

      {showClearConfirm && (
        <ConfirmModal
          title="Clear History"
          message="This will permanently delete all check history. This action cannot be undone."
          confirmLabel="Clear All"
          danger
          onConfirm={handleClear}
          onCancel={() => setShowClearConfirm(false)}
        />
      )}
    </div>
  );
}
