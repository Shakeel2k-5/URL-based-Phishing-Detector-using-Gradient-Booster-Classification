export default function FeedbackButtons({ result, onFeedback, feedbackGiven, loading }) {
  if (!result) return null;

  if (feedbackGiven) {
    return (
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 text-sm text-indigo-700">
        Thank you for your feedback! The correction has been recorded.
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <p className="text-sm text-gray-600 mb-3">Is this prediction correct?</p>
      <div className="flex flex-wrap gap-3">
        {result.safe ? (
          <button
            onClick={() => onFeedback(-1)}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Submitting...' : 'Report as Phishing'}
          </button>
        ) : (
          <button
            onClick={() => onFeedback(1)}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Submitting...' : 'Report as Safe'}
          </button>
        )}
      </div>
    </div>
  );
}
