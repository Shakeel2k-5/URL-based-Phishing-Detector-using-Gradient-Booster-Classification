import { useState } from 'react';
import { retrainModel } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import Card from '../common/Card';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import ConfirmModal from '../common/ConfirmModal';

export default function RetrainPanel() {
  const { loading, error, execute, clearError } = useApi();
  const [result, setResult] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleRetrain = async () => {
    setShowConfirm(false);
    setResult(null);
    try {
      const data = await execute(() => retrainModel());
      setResult(data);
    } catch {
      // error is handled by useApi
    }
  };

  return (
    <>
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Retrain Model</h3>
        <p className="text-sm text-gray-600 mb-6">
          Retrain the phishing detection model using the original dataset combined with any
          user-submitted feedback. This process may take a few minutes.
        </p>

        <ErrorAlert message={error} onDismiss={clearError} />

        {loading ? (
          <LoadingSpinner label="Retraining model... this may take a few minutes" />
        ) : (
          <button
            onClick={() => setShowConfirm(true)}
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Retrain Model
          </button>
        )}

        {result && (
          <div className="mt-6 bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-emerald-700 mb-2">Retraining Complete</p>
            <div className="text-sm text-emerald-600 space-y-1">
              {result.message && <p>{result.message}</p>}
              {result.samples && <p>Training samples: {result.samples}</p>}
              {result.accuracy && <p>Model accuracy: {(result.accuracy * 100).toFixed(2)}%</p>}
            </div>
          </div>
        )}
      </Card>

      {showConfirm && (
        <ConfirmModal
          title="Retrain Model"
          message="This will retrain the phishing detection model with all available data including user feedback. This process may take several minutes. Continue?"
          confirmLabel="Start Retraining"
          onConfirm={handleRetrain}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  );
}
