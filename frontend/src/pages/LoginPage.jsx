/**
 * LoginPage — AudienceFlow
 *
 * Wired to POST /auth/login.
 * Accepts navigation state { email, registered: true } from RegisterPage
 * to pre-fill the email field and show a success banner.
 */
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Activity, Eye, EyeOff, Mail, Lock,
  AlertCircle, CheckCircle, Loader2,
} from 'lucide-react';
import { loginUser } from '../services/api';
import '../styles/landing.css';

// ── Validation ────────────────────────────────────────────────────────────────
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(fields) {
  const errors = {};
  if (!fields.email.trim())
    errors.email = 'Email address is required.';
  else if (!EMAIL_RE.test(fields.email.trim()))
    errors.email = 'Please enter a valid email address.';
  if (!fields.password)
    errors.password = 'Password is required.';
  return errors;
}

// ── Extract readable error from Axios error ───────────────────────────────────
function extractError(err) {
  if (!err.response) return 'Unable to connect to the server. Please try again.';
  const { status, data } = err.response;
  if (status === 401) return 'Invalid email or password. Please try again.';
  if (status === 503) return 'Service temporarily unavailable. Please try again shortly.';
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail))
    return data.detail.map((d) => d.msg).join(' | ');
  return 'Login failed. Please try again.';
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function LoginPage() {
  const location  = useLocation();
  const navigate  = useNavigate();

  const fromRegister = location.state?.registered === true;
  const prefillEmail = location.state?.email || '';

  const [fields,       setFields]       = useState({ email: prefillEmail, password: '' });
  const [errors,       setErrors]       = useState({});
  const [apiError,     setApiError]     = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting,   setSubmitting]   = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFields((p) => ({ ...p, [name]: value }));
    setApiError('');
    if (errors[name]) setErrors((p) => ({ ...p, [name]: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    const errs = validate(fields);
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }

    setSubmitting(true);
    try {
      const data = await loginUser({
        email:    fields.email.trim().toLowerCase(),
        password: fields.password,
      });
      // Store JWT token for future authenticated requests
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      setLoggedInUser(data.user);
      // Redirect to dashboard after 1.2 s
      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      setApiError(extractError(err));
    } finally {
      setSubmitting(false);
    }
  };

  // ── Success screen ────────────────────────────────────────────────────────
  if (loggedInUser) {
    return (
      <div className="auth-page">
        <div className="auth-card" style={{ textAlign: 'center' }}>
          <div className="auth-logo" style={{ justifyContent: 'center' }}>
            <div className="auth-logo-icon">
              <Activity size={20} color="white" strokeWidth={2.5} />
            </div>
            <span className="auth-logo-text">AudienceFlow</span>
          </div>

          <div style={{
            width: 72, height: 72, borderRadius: '50%',
            background: 'var(--color-success-bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto var(--space-4)',
          }}>
            <CheckCircle size={36} color="var(--color-success)" />
          </div>

          <h2 className="auth-title" style={{ color: 'var(--color-success)' }}>
            Welcome back!
          </h2>
          <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-2)' }}>
            Signed in as <strong>{loggedInUser.name}</strong>
          </p>
          <p style={{ color: 'var(--color-gray-400)', fontSize: 'var(--text-xs)', marginBottom: 'var(--space-6)' }}>
            Role: {loggedInUser.role} &bull; {loggedInUser.email}
          </p>

          <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)',
            background: 'var(--color-blue-soft)', borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-3) var(--space-4)', textAlign: 'left' }}>
            ℹ️ Dashboard and JWT session management will be available in Milestone 2.
          </p>

          <button
            className="btn btn-outline"
            style={{ width: '100%' }}
            onClick={() => {
              localStorage.removeItem('access_token');
              setLoggedInUser(null);
              setFields({ email: '', password: '' });
            }}
          >
            Sign out
          </button>

          <p className="auth-footer" style={{ marginTop: 'var(--space-4)' }}>
            <Link to="/">← Back to home</Link>
          </p>
        </div>
      </div>
    );
  }

  // ── Main form ─────────────────────────────────────────────────────────────
  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* Logo */}
        <Link to="/" className="auth-logo" aria-label="AudienceFlow home">
          <div className="auth-logo-icon">
            <Activity size={20} color="white" strokeWidth={2.5} />
          </div>
          <span className="auth-logo-text">AudienceFlow</span>
        </Link>

        {/* Registration success banner */}
        {fromRegister && (
          <div role="status" style={{
            background: 'var(--color-success-bg)',
            border: '1px solid var(--color-success)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-3) var(--space-4)',
            display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)',
            marginBottom: 'var(--space-5)', fontSize: 'var(--text-sm)', color: '#065F46',
          }}>
            <CheckCircle size={16} style={{ flexShrink: 0, marginTop: 1, color: 'var(--color-success)' }} />
            <span>
              <strong>Registration successful!</strong> Your account is ready — sign in below.
            </span>
          </div>
        )}

        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your AudienceFlow account</p>

        {/* API error banner */}
        {apiError && (
          <div role="alert" style={{
            background: 'var(--color-error-bg)', border: '1px solid var(--color-error)',
            borderRadius: 'var(--radius-lg)', padding: 'var(--space-3) var(--space-4)',
            display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)',
            marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)', color: 'var(--color-error)',
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
            <span>{apiError}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate aria-label="Login form">

          {/* Email */}
          <div className="form-group">
            <label htmlFor="login-email" className="form-label">
              <Mail size={14} style={{ display: 'inline', marginRight: 4 }} aria-hidden="true" />
              Email Address
            </label>
            <input
              id="login-email" type="email" name="email"
              className={`form-input${errors.email ? ' error' : ''}`}
              placeholder="you@example.com"
              value={fields.email} onChange={handleChange}
              autoComplete="email" aria-required="true"
              aria-invalid={!!errors.email}
              disabled={submitting}
            />
            {errors.email && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} aria-hidden="true" /> {errors.email}
              </span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="login-password" className="form-label">
              <Lock size={14} style={{ display: 'inline', marginRight: 4 }} aria-hidden="true" />
              Password
            </label>
            <div className="auth-password-wrap">
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                className={`form-input${errors.password ? ' error' : ''}`}
                placeholder="Enter your password"
                value={fields.password} onChange={handleChange}
                autoComplete="current-password" aria-required="true"
                aria-invalid={!!errors.password}
                disabled={submitting}
              />
              <button
                type="button" className="auth-password-toggle"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}
              </button>
            </div>
            {errors.password && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} aria-hidden="true" /> {errors.password}
              </span>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={submitting}
            style={{ opacity: submitting ? 0.75 : 1, cursor: submitting ? 'not-allowed' : 'pointer' }}
          >
            {submitting ? (
              <>
                <Loader2 size={16} style={{ animation: 'spin 1s linear infinite', marginRight: 6 }} aria-hidden="true" />
                Signing in…
              </>
            ) : (
              'Sign In'
            )}
          </button>

        </form>

        <p className="auth-footer">
          Don&apos;t have an account?{' '}
          <Link to="/register">Create one free</Link>
        </p>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
