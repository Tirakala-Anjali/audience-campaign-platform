import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CampaignsPage from './pages/CampaignsPage';
import DashboardPage from './pages/DashboardPage';
import { checkHealth } from './services/api';

/**
 * apiStatus shape:
 *   { state: 'loading' | 'connected' | 'disconnected', label: string }
 */
function useApiStatus() {
  const [apiStatus, setApiStatus] = useState({ state: 'loading', label: 'Checking API…' });

  useEffect(() => {
    let cancelled = false;

    checkHealth()
      .then((data) => {
        if (cancelled) return;
        const dbLabel = data.database === 'connected' ? ' · DB ✓' : ' · DB ✗';
        setApiStatus({
          state: 'connected',
          label: `API Connected ✓${dbLabel}`,
        });
        console.info('[AudienceFlow] Backend health:', data);
      })
      .catch((err) => {
        if (cancelled) return;
        setApiStatus({ state: 'disconnected', label: 'API Offline' });
        console.warn('[AudienceFlow] Backend unreachable:', err.message);
      });

    return () => { cancelled = true; };
  }, []);

  return apiStatus;
}

/**
 * ProtectedRoute — redirects to /login if no JWT token in localStorage.
 */
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const apiStatus = useApiStatus();

  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page — full layout with Navbar + Footer */}
        <Route
          path="/"
          element={
            <MainLayout>
              <LandingPage apiStatus={apiStatus} />
            </MainLayout>
          }
        />

        {/* Auth pages — standalone layout */}
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected app pages */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/campaigns"
          element={
            <ProtectedRoute>
              <CampaignsPage />
            </ProtectedRoute>
          }
        />

        {/* 404 fallback */}
        <Route
          path="*"
          element={
            <MainLayout>
              <div
                style={{
                  minHeight: '60vh',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--space-4)',
                  textAlign: 'center',
                  padding: 'var(--space-8)',
                }}
              >
                <h1 style={{ fontSize: 'var(--text-5xl)', fontWeight: 800, color: 'var(--color-navy)' }}>
                  404
                </h1>
                <p style={{ fontSize: 'var(--text-xl)', color: 'var(--color-gray-500)' }}>
                  Page not found.
                </p>
                <a href="/" className="btn btn-primary">Go Home</a>
              </div>
            </MainLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
