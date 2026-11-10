/**
 * RegisterPage — AudienceFlow
 *
 * Full registration form connected to POST /auth/register.
 * Roles are loaded from GET /auth/roles on mount.
 * On success: redirects to /login with email pre-filled via state.
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity, Eye, EyeOff, User, Mail, Phone,
  Building2, Lock, AlertCircle, CheckCircle, Loader2,
} from 'lucide-react';
import { getRoles, registerUser } from '../services/api';
import '../styles/landing.css';

// ─── Validation helpers ───────────────────────────────────────────────────

const EMAIL_RE   = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE   = /^\+?[0-9\s\-().]{7,20}$/;
const STRONG_PW  = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

function validate(fields) {
  const e = {};

  if (!fields.name.trim())
    e.name = 'Full name is required.';
  else if (fields.name.trim().length < 2)
    e.name = 'Name must be at least 2 characters.';

  if (!fields.email.trim())
    e.email = 'Email address is required.';
  else if (!EMAIL_RE.test(fields.email.trim()))
    e.email = 'Please enter a valid email address.';

  if (!fields.phone.trim())
    e.phone = 'Phone number is required.';
  else if (!PHONE_RE.test(fields.phone.trim()))
    e.phone = 'Please enter a valid phone number (7–20 digits).';

  if (!fields.organization_name.trim())
    e.organization_name = 'Organisation name is required.';

  if (!fields.role)
    e.role = 'Please select a role.';

  if (!fields.password)
    e.password = 'Password is required.';
  else if (!STRONG_PW.test(fields.password))
    e.password = 'Password must be 8+ characters with uppercase, lowercase, number, and special character.';

  if (!fields.confirmPassword)
    e.confirmPassword = 'Please confirm your password.';
  else if (fields.password !== fields.confirmPassword)
    e.confirmPassword = 'Passwords do not match.';

  return e;
}

// ─── Password strength ────────────────────────────────────────────────────

function getStrength(pw) {
  if (!pw) return { score: 0, label: '', color: '' };
  let s = 0;
  if (pw.length >= 8)              s++;
  if (pw.length >= 12)             s++;
  if (/[A-Z]/.test(pw))            s++;
  if (/[0-9]/.test(pw))            s++;
  if (/[^A-Za-z0-9]/.test(pw))    s++;
  if (s <= 1) return { score: s, label: 'Weak',   color: '#EF4444' };
  if (s <= 2) return { score: s, label: 'Fair',   color: '#F59E0B' };
  if (s <= 3) return { score: s, label: 'Good',   color: '#3B82F6' };
  return           { score: s, label: 'Strong', color: '#10B981' };
}

// ─── Extract readable error message from Axios error ─────────────────────

function extractApiError(err) {
  if (!err.response) return 'Unable to connect to the server. Please try again.';
  const { status, data } = err.response;
  if (status === 409) return 'An account with this email already exists. Please use another email or log in.';
  if (status === 422 && Array.isArray(data?.detail)) {
    // Pydantic validation errors — map field messages
    return data.detail.map((d) => d.msg).join(' | ');
  }
  if (typeof data?.detail === 'string') return data.detail;
  if (status >= 500) return 'Registration failed due to a server error. Please try again.';
  return 'Registration failed. Please check your details and try again.';
}

// ─── Component ────────────────────────────────────────────────────────────

export default function RegisterPage() {
  const navigate = useNavigate();

  const [fields, setFields] = useState({
    name: '', email: '', phone: '', organization_name: '',
    role: '', password: '', confirmPassword: '',
  });
  const [errors,       setErrors]       = useState({});
  const [apiError,     setApiError]     = useState('');
  const [submitting,   setSubmitting]   = useState(false);
  const [success,      setSuccess]      = useState(false);
  const [showPw,       setShowPw]       = useState(false);
  const [showConfirm,  setShowConfirm]  = useState(false);
  const [roles,        setRoles]        = useState([]);
  const [rolesLoading, setRolesLoading] = useState(true);

  const strength = getStrength(fields.password);

  // ── Load roles from backend on mount ─────────────────────────────────
  useEffect(() => {
    let alive = true;
    setRolesLoading(true);
    getRoles()
      .then((data) => { if (alive) setRoles(data); })
      .catch(() => {
        if (alive)
          setRoles([
            { id: 1, name: 'Campaign Manager' },
            { id: 2, name: 'Communication Team' },
          ]);
      })
      .finally(() => { if (alive) setRolesLoading(false); });
    return () => { alive = false; };
  }, []);

  // ── Field change — clear that field's error ───────────────────────────
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFields((p) => ({ ...p, [name]: value }));
    setApiError('');
    if (errors[name]) setErrors((p) => ({ ...p, [name]: '' }));
  };

  // ── Submit ────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');

    // Client-side validation
    const errs = validate(fields);
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      // Scroll to the first error
      const first = document.querySelector('.form-input.error, select.form-input.error');
      first?.focus();
      return;
    }

    setSubmitting(true);
    try {
      await registerUser({
        name:              fields.name.trim(),
        email:             fields.email.trim().toLowerCase(),
        phone:             fields.phone.trim(),
        organization_name: fields.organization_name.trim(),
        password:          fields.password,
        role:              fields.role,
      });

      setSuccess(true);
      // Redirect to login after 2 s, passing email for pre-fill
      setTimeout(() => {
        navigate('/login', { state: { email: fields.email.trim(), registered: true } });
      }, 2000);
    } catch (err) {
      setApiError(extractApiError(err));
      // If 409, highlight email field
      if (err.response?.status === 409) {
        setErrors((p) => ({ ...p, email: 'This email is already registered.' }));
      }
    } finally {
      setSubmitting(false);
    }
  };

  // ── Success screen ────────────────────────────────────────────────────
  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card" style={{ textAlign: 'center' }}>
          <div style={{
            width: 72, height: 72, borderRadius: '50%',
            background: 'var(--color-success-bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto var(--space-5)',
          }}>
            <CheckCircle size={36} color="var(--color-success)" />
          </div>
          <h2 className="auth-title" style={{ color: 'var(--color-success)' }}>
            Registration Successful!
          </h2>
          <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Your account has been created. Redirecting to login…
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-4)' }}>
            <Loader2 size={22} color="var(--color-purple)"
              style={{ animation: 'spin 1s linear infinite' }} />
          </div>
          <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>
            Go to Login now
          </Link>
        </div>
        {/* spin keyframe */}
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  // ── Main form ─────────────────────────────────────────────────────────
  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* Logo */}
        <Link to="/" className="auth-logo" aria-label="AudienceFlow home">
          <div className="auth-logo-icon"><Activity size={20} color="white" strokeWidth={2.5} /></div>
          <span className="auth-logo-text">AudienceFlow</span>
        </Link>

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join AudienceFlow — it's free to get started</p>

        {/* Global API error banner */}
        {apiError && (
          <div role="alert" style={{
            background: 'var(--color-error-bg)', border: '1px solid var(--color-error)',
            borderRadius: 'var(--radius-lg)', padding: 'var(--space-3) var(--space-4)',
            display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)',
            marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)',
            color: 'var(--color-error)',
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
            <span>{apiError}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate aria-label="Registration form">

          {/* ── Full Name ──────────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-name" className="form-label">
              <User size={13} style={{ display:'inline', marginRight:4 }} />
              Full Name <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <input
              id="reg-name" type="text" name="name"
              className={`form-input${errors.name ? ' error' : ''}`}
              placeholder="Jane Doe"
              value={fields.name} onChange={handleChange}
              autoComplete="name" aria-required="true"
              aria-invalid={!!errors.name}
              disabled={submitting}
            />
            {errors.name && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.name}
              </span>
            )}
          </div>

          {/* ── Email ─────────────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-email" className="form-label">
              <Mail size={13} style={{ display:'inline', marginRight:4 }} />
              Email Address <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <input
              id="reg-email" type="email" name="email"
              className={`form-input${errors.email ? ' error' : ''}`}
              placeholder="you@example.com"
              value={fields.email} onChange={handleChange}
              autoComplete="email" aria-required="true"
              aria-invalid={!!errors.email}
              disabled={submitting}
            />
            {errors.email && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.email}
              </span>
            )}
          </div>

          {/* ── Phone ─────────────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-phone" className="form-label">
              <Phone size={13} style={{ display:'inline', marginRight:4 }} />
              Phone Number <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <input
              id="reg-phone" type="tel" name="phone"
              className={`form-input${errors.phone ? ' error' : ''}`}
              placeholder="9876543210"
              value={fields.phone} onChange={handleChange}
              autoComplete="tel" aria-required="true"
              aria-invalid={!!errors.phone}
              disabled={submitting}
            />
            {errors.phone && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.phone}
              </span>
            )}
          </div>

          {/* ── Organisation ──────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-org" className="form-label">
              <Building2 size={13} style={{ display:'inline', marginRight:4 }} />
              Organisation Name <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <input
              id="reg-org" type="text" name="organization_name"
              className={`form-input${errors.organization_name ? ' error' : ''}`}
              placeholder="Example Organisation"
              value={fields.organization_name} onChange={handleChange}
              autoComplete="organization" aria-required="true"
              aria-invalid={!!errors.organization_name}
              disabled={submitting}
            />
            {errors.organization_name && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.organization_name}
              </span>
            )}
          </div>

          {/* ── Role ──────────────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-role" className="form-label">
              Role <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <select
              id="reg-role" name="role"
              className={`form-input${errors.role ? ' error' : ''}`}
              value={fields.role} onChange={handleChange}
              aria-required="true" aria-invalid={!!errors.role}
              disabled={submitting || rolesLoading}
              style={{ cursor: submitting || rolesLoading ? 'not-allowed' : 'pointer' }}
            >
              <option value="">
                {rolesLoading ? 'Loading roles…' : '— Select your role —'}
              </option>
              {roles.map((r) => (
                <option key={r.id} value={r.name}>{r.name}</option>
              ))}
            </select>
            {errors.role && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.role}
              </span>
            )}
          </div>

          {/* ── Password ──────────────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-password" className="form-label">
              <Lock size={13} style={{ display:'inline', marginRight:4 }} />
              Password <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <div className="auth-password-wrap">
              <input
                id="reg-password"
                type={showPw ? 'text' : 'password'}
                name="password"
                className={`form-input${errors.password ? ' error' : ''}`}
                placeholder="Min 8 chars, upper, lower, number, symbol"
                value={fields.password} onChange={handleChange}
                autoComplete="new-password" aria-required="true"
                aria-invalid={!!errors.password}
                disabled={submitting}
              />
              <button type="button" className="auth-password-toggle"
                onClick={() => setShowPw((v) => !v)}
                aria-label={showPw ? 'Hide password' : 'Show password'}>
                {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {/* Strength bar */}
            {fields.password && (
              <div aria-live="polite" style={{ marginTop: 'var(--space-2)' }}>
                <div style={{
                  height: 5, borderRadius: 999, background: 'var(--color-gray-200)',
                }}>
                  <div style={{
                    height: '100%', borderRadius: 999,
                    width: `${(strength.score / 5) * 100}%`,
                    background: strength.color,
                    transition: 'width .3s ease, background .3s ease',
                  }} />
                </div>
                <p style={{ fontSize: 'var(--text-xs)', color: strength.color,
                  marginTop: 'var(--space-1)', fontWeight: 600 }}>
                  {strength.label} password
                </p>
              </div>
            )}

            {errors.password && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.password}
              </span>
            )}
          </div>

          {/* ── Confirm Password ──────────────────────────────────────── */}
          <div className="form-group">
            <label htmlFor="reg-confirm" className="form-label">
              <Lock size={13} style={{ display:'inline', marginRight:4 }} />
              Confirm Password <span style={{ color:'var(--color-error)' }}>*</span>
            </label>
            <div className="auth-password-wrap">
              <input
                id="reg-confirm"
                type={showConfirm ? 'text' : 'password'}
                name="confirmPassword"
                className={`form-input${errors.confirmPassword ? ' error' : ''}`}
                placeholder="Repeat your password"
                value={fields.confirmPassword} onChange={handleChange}
                autoComplete="new-password" aria-required="true"
                aria-invalid={!!errors.confirmPassword}
                disabled={submitting}
              />
              <button type="button" className="auth-password-toggle"
                onClick={() => setShowConfirm((v) => !v)}
                aria-label={showConfirm ? 'Hide confirm password' : 'Show confirm password'}>
                {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {errors.confirmPassword && (
              <span className="form-error" role="alert">
                <AlertCircle size={13} /> {errors.confirmPassword}
              </span>
            )}
            {fields.confirmPassword && !errors.confirmPassword &&
              fields.password === fields.confirmPassword && (
              <span style={{ fontSize:'var(--text-xs)', color:'var(--color-success)',
                display:'flex', alignItems:'center', gap:4, marginTop:'var(--space-1)' }}>
                <CheckCircle size={13} /> Passwords match
              </span>
            )}
          </div>

          {/* ── Submit ────────────────────────────────────────────────── */}
          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={submitting}
            style={{ opacity: submitting ? 0.75 : 1, cursor: submitting ? 'not-allowed' : 'pointer' }}
          >
            {submitting ? (
              <>
                <Loader2 size={16}
                  style={{ animation: 'spin 1s linear infinite', marginRight: 6 }} />
                Creating your account…
              </>
            ) : (
              'Create Account'
            )}
          </button>

        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
