import { useState } from 'react';

export default function UrlInput({ onSubmit, loading }) {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) {
      setValidationError('Please enter a URL');
      return;
    }
    if (!/^https?:\/\/.+/i.test(trimmed)) {
      setValidationError('URL must start with http:// or https://');
      return;
    }
    setValidationError('');
    onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (validationError) setValidationError('');
            }}
            placeholder="Enter URL to check (e.g., https://example.com)"
            disabled={loading}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:text-gray-400 transition-colors"
          />
          {validationError && (
            <p className="absolute -bottom-6 left-0 text-xs text-red-500">{validationError}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed transition-colors shrink-0"
        >
          {loading ? 'Analyzing...' : 'Check URL'}
        </button>
      </div>
    </form>
  );
}
