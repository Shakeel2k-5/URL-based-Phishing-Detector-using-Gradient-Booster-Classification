import { createContext, useReducer, useEffect } from 'react';

export const HistoryContext = createContext(null);

const STORAGE_KEY = 'phishing-detector-history';

const initialState = { checks: [] };

function historyReducer(state, action) {
  switch (action.type) {
    case 'ADD_CHECK':
      return { checks: [action.payload, ...state.checks] };
    case 'ADD_FEEDBACK':
      return {
        checks: state.checks.map((c) =>
          c.id === action.payload.id
            ? { ...c, feedbackGiven: action.payload.feedback }
            : c
        ),
      };
    case 'DELETE_CHECK':
      return { checks: state.checks.filter((c) => c.id !== action.payload) };
    case 'CLEAR_HISTORY':
      return { checks: [] };
    default:
      return state;
  }
}

function loadState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : initialState;
  } catch {
    return initialState;
  }
}

export function HistoryProvider({ children }) {
  const [state, dispatch] = useReducer(historyReducer, null, loadState);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const addCheck = (result) => {
    dispatch({
      type: 'ADD_CHECK',
      payload: {
        id: crypto.randomUUID(),
        url: result.url,
        prediction: result.prediction,
        safe: result.safe,
        feedbackGiven: null,
        checkedAt: new Date().toISOString(),
      },
    });
  };

  const addFeedback = (checkId, feedback) => {
    dispatch({ type: 'ADD_FEEDBACK', payload: { id: checkId, feedback } });
  };

  const deleteCheck = (checkId) => {
    dispatch({ type: 'DELETE_CHECK', payload: checkId });
  };

  const clearHistory = () => {
    dispatch({ type: 'CLEAR_HISTORY' });
  };

  const getStats = () => {
    const { checks } = state;
    const total = checks.length;
    const safe = checks.filter((c) => c.safe).length;
    const phishing = total - safe;
    const feedbackCount = checks.filter((c) => c.feedbackGiven !== null).length;

    const today = new Date().toDateString();
    const todayChecks = checks.filter(
      (c) => new Date(c.checkedAt).toDateString() === today
    ).length;

    return {
      total,
      safe,
      phishing,
      safetyRate: total > 0 ? ((safe / total) * 100).toFixed(1) : '0.0',
      feedbackCount,
      todayChecks,
    };
  };

  return (
    <HistoryContext.Provider
      value={{
        checks: state.checks,
        addCheck,
        addFeedback,
        deleteCheck,
        clearHistory,
        getStats,
      }}
    >
      {children}
    </HistoryContext.Provider>
  );
}
