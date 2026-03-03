import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import UrlInput from '../components/url-checker/UrlInput';
import ResultCard from '../components/url-checker/ResultCard';
import FeedbackButtons from '../components/url-checker/FeedbackButtons';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { predictUrl, submitFeedback } from '../api/client';
import { useHistory } from '../hooks/useHistory';
import { useApi } from '../hooks/useApi';

export default function CheckUrlPage() {
  const location = useLocation();
  const { addCheck, addFeedback, checks } = useHistory();
  const predictApi = useApi();
  const feedbackApi = useApi();

  const [result, setResult] = useState(location.state?.result || null);
  const [feedbackGiven, setFeedbackGiven] = useState(null);

  const handleCheck = async (url) => {
    setResult(null);
    setFeedbackGiven(null);
    try {
      const data = await predictApi.execute(() => predictUrl(url));
      setResult(data);
      addCheck(data);
    } catch {
      // error handled by useApi
    }
  };

  const handleFeedback = async (actualClass) => {
    if (!result) return;
    try {
      await feedbackApi.execute(() => submitFeedback(result.url, actualClass));
      const feedbackType = actualClass === 1 ? 'safe' : 'phishing';
      setFeedbackGiven(feedbackType);
      const check = checks.find((c) => c.url === result.url && c.feedbackGiven === null);
      if (check) {
        addFeedback(check.id, feedbackType);
      }
    } catch {
      // error handled by useApi
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Check URL</h1>
        <p className="text-gray-500">Enter a URL to analyze it for phishing indicators</p>
      </div>

      <UrlInput onSubmit={handleCheck} loading={predictApi.loading} />

      {predictApi.error && (
        <ErrorAlert message={predictApi.error} onDismiss={predictApi.clearError} />
      )}

      {predictApi.loading && (
        <LoadingSpinner label="Analyzing URL features... this may take up to 30 seconds" />
      )}

      {result && !predictApi.loading && (
        <div className="space-y-4">
          <ResultCard result={result} />
          <FeedbackButtons
            result={result}
            onFeedback={handleFeedback}
            feedbackGiven={feedbackGiven}
            loading={feedbackApi.loading}
          />
          {feedbackApi.error && (
            <ErrorAlert message={feedbackApi.error} onDismiss={feedbackApi.clearError} />
          )}
        </div>
      )}
    </div>
  );
}
