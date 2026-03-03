import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HistoryProvider } from './context/HistoryContext';
import Navbar from './components/layout/Navbar';
import PageLayout from './components/layout/PageLayout';
import DashboardPage from './pages/DashboardPage';
import CheckUrlPage from './pages/CheckUrlPage';
import HistoryPage from './pages/HistoryPage';
import AdminPage from './pages/AdminPage';

export default function App() {
  return (
    <HistoryProvider>
      <BrowserRouter>
        <Navbar />
        <PageLayout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/check" element={<CheckUrlPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </PageLayout>
      </BrowserRouter>
    </HistoryProvider>
  );
}
