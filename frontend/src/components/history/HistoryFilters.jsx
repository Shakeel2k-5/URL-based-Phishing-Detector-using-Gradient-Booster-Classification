export default function HistoryFilters({ search, onSearchChange, filter, onFilterChange, onClear, total }) {
  return (
    <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
      <div className="flex flex-col sm:flex-row gap-3 flex-1 w-full sm:w-auto">
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search URLs..."
          className="px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm text-gray-900 placeholder-gray-400 w-full sm:w-64"
        />
        <select
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
          className="px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm text-gray-700 bg-white"
        >
          <option value="all">All Results</option>
          <option value="safe">Safe Only</option>
          <option value="phishing">Phishing Only</option>
        </select>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">{total} results</span>
        <button
          onClick={onClear}
          className="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  );
}
