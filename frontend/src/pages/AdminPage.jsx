import { useState, useEffect } from 'react';
import RetrainPanel from '../components/admin/RetrainPanel';
import Card from '../components/common/Card';
import { checkHealth } from '../api/client';

export default function AdminPage() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkHealth()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Admin Panel</h1>
        <p className="text-gray-500">Manage the phishing detection model and system</p>
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">API Status</h3>
        <div className="flex items-center gap-3">
          <span
            className={`w-3 h-3 rounded-full ${
              apiStatus === 'online'
                ? 'bg-emerald-500'
                : apiStatus === 'offline'
                  ? 'bg-red-500'
                  : 'bg-amber-500 animate-pulse'
            }`}
          />
          <span className="text-sm text-gray-700 font-medium">
            {apiStatus === 'online'
              ? 'Backend API is running'
              : apiStatus === 'offline'
                ? 'Backend API is unreachable'
                : 'Checking API status...'}
          </span>
          {apiStatus !== 'checking' && (
            <button
              onClick={() => {
                setApiStatus('checking');
                checkHealth()
                  .then(() => setApiStatus('online'))
                  .catch(() => setApiStatus('offline'));
              }}
              className="text-sm text-indigo-600 hover:text-indigo-800 ml-auto"
            >
              Refresh
            </button>
          )}
        </div>
      </Card>

      <RetrainPanel />
    </div>
  );
}
