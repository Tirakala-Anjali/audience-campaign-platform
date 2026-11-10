import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/global.css';
import App from './App';

const container = document.getElementById('root');

if (!container) {
  throw new Error(
    '[AudienceFlow] Root element #root not found. Check index.html.'
  );
}

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>
);
