const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/`);
  if (!res.ok) throw new Error('API not reachable');
  return res.json();
}

export async function predictUrl(url) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Prediction failed');
  }
  return res.json();
}

export async function submitFeedback(url, actualClass) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, actual_class: actualClass }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Feedback submission failed');
  }
  return res.json();
}

export async function retrainModel() {
  const res = await fetch(`${API_BASE}/retrain`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Retrain request failed');
  return res.json();
}
