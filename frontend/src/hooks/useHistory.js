import { useContext } from 'react';
import { HistoryContext } from '../context/HistoryContext';

export function useHistory() {
  return useContext(HistoryContext);
}
