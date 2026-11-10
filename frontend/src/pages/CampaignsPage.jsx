/**
 * CampaignsPage — AudienceFlow
 *
 * Protected page. Requires a valid JWT token in localStorage.
 * Provides full CRUD: list, create, edit, delete campaigns.
 */
import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity, Plus, Pencil, Trash2, AlertCircle,
  CheckCircle, Loader2, RefreshCw, LogOut,
} from 'lucide-react';
import {
  getCampaigns, createCampaign, updateCampaign, deleteCampaign, getMe, logout,
} from '../services/api';
import '../styles/landing.css';
import '../styles/campaigns.css';

const STATUS_OPTIONS = ['draft', 'active', 'paused', 'completed', 'cancelled'];

const STATUS_COLORS = {
  draft:     { bg: '#F3F4F6', color: '#6B7280' },
  active:    { bg: '#D1FAE5', color: '#065F46' },
  paused:    { bg: '#FEF3C7', color: '#92400E' },
  completed: { bg: '#DBEAFE', color: '#1E40AF' },
  cancelled: { bg: '#FEE2E2', color: '#991B1B' },
};

const EMPTY_FORM = { name: '', description: '', status: 'draft', start_at: '', end_at: '' };

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS.draft;
  return (
    <span style={{
      background: c.bg, color: c.color,
      padding: '2px 10px', borderRadius: 999,
      fontSize: 'var(--text-xs)', fontWeight: 600,
      textTransform: 'capitalize',
    }}>
      {status}
    </span>
  );
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function CampaignsPage() {
  const navigate = useNavigate();

  const [user,       setUser]       = useState(null);
  const [campaigns,  setCampaigns]  = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState('');
  const [showForm,   setShowForm]   = useState(false);
  const [editId,     setEditId]     = useState(null);
  const [form,       setForm]       = useState(EMPTY_FORM);
  const [formError,  setFormError]  = useState('');
  const [saving,     setSaving]     = useState(false);
  const [deleteId,   setDeleteId]   = useState(null);
  const [deleting,   setDeleting]   = useState(false);
  const [toast,      setToast]      = useState('');

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  // ── Auth check ────────────────────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { navigate('/login'); return; }
    getMe()
      .then(setUser)
      .catch(() => { localStorage.removeItem('access_token'); navigate('/login'); });
  }, [navigate]);

  // ── Load campaigns ────────────────────────────────────────────────────────
  const loadCampaigns = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const data = await getCampaigns();
      setCampaigns(data);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token'); navigate('/login');
      } else {
        setError('Failed to load campaigns. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => { if (user) loadCampaigns(); }, [user, loadCampaigns]);

  // ── Form handlers ─────────────────────────────────────────────────────────
  const openCreate = () => {
    setEditId(null); setForm(EMPTY_FORM); setFormError(''); setShowForm(true);
  };

  const openEdit = (c) => {
    setEditId(c.id);
    setForm({
      name:        c.name,
      description: c.description || '',
      status:      c.status,
      start_at:    c.start_at ? c.start_at.slice(0, 16) : '',
      end_at:      c.end_at   ? c.end_at.slice(0, 16)   : '',
    });
    setFormError(''); setShowForm(true);
  };

  const closeForm = () => { setShowForm(false); setEditId(null); setForm(EMPTY_FORM); setFormError(''); };

  const handleFormChange = (e) => {
    setForm(p => ({ ...p, [e.target.name]: e.target.value }));
    setFormError('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) { setFormError('Campaign name is required.'); return; }

    setSaving(true); setFormError('');
    const payload = {
      name:        form.name.trim(),
      description: form.description.trim() || null,
      status:      form.status,
      start_at:    form.start_at || null,
      end_at:      form.end_at   || null,
    };

    try {
      if (editId) {
        await updateCampaign(editId, payload);
        showToast('Campaign updated ✓');
      } else {
        await createCampaign(payload);
        showToast('Campaign created ✓');
      }
      closeForm();
      loadCampaigns();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(typeof detail === 'string' ? detail : 'Save failed. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // ── Delete ────────────────────────────────────────────────────────────────
  const confirmDelete = (id) => setDeleteId(id);
  const cancelDelete  = ()   => setDeleteId(null);

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await deleteCampaign(deleteId);
      setDeleteId(null);
      showToast('Campaign deleted ✓');
      loadCampaigns();
    } catch {
      showToast('Delete failed. Please try again.');
      setDeleteId(null);
    } finally {
      setDeleting(false);
    }
  };

  // ── Logout ────────────────────────────────────────────────────────────────
  const handleLogout = () => { logout(); navigate('/login'); };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-off-white)' }}>

      {/* ── Header ──────────────────────────────────────────────────── */}
      <header style={{
        background: 'var(--color-navy)', padding: 'var(--space-4) var(--space-8)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--color-purple), #06B6D4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Activity size={18} color="white" />
          </div>
          <span style={{ color: 'white', fontWeight: 700, fontSize: 'var(--text-lg)' }}>
            AudienceFlow
          </span>
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {user && (
            <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: 'var(--text-sm)' }}>
              {user.name} · {user.role}
            </span>
          )}
          <button
            onClick={handleLogout}
            className="btn btn-outline-white btn-sm"
            aria-label="Log out"
          >
            <LogOut size={14} aria-hidden="true" /> Log out
          </button>
        </div>
      </header>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <main style={{ maxWidth: 1100, margin: '0 auto', padding: 'var(--space-8)' }}>

        {/* Page title row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
          <div>
            <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: 'var(--color-navy)', margin: 0 }}>
              Campaigns
            </h1>
            <p style={{ color: 'var(--color-gray-500)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
              {campaigns.length} campaign{campaigns.length !== 1 ? 's' : ''}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <button className="btn btn-outline btn-sm" onClick={loadCampaigns} aria-label="Refresh">
              <RefreshCw size={14} aria-hidden="true" /> Refresh
            </button>
            <button className="btn btn-primary" onClick={openCreate}>
              <Plus size={16} aria-hidden="true" /> New Campaign
            </button>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div role="alert" style={{
            background: 'var(--color-error-bg)', border: '1px solid var(--color-error)',
            borderRadius: 'var(--radius-lg)', padding: 'var(--space-3) var(--space-4)',
            display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-4)',
            color: 'var(--color-error)', fontSize: 'var(--text-sm)',
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: 'var(--space-16)', color: 'var(--color-gray-400)' }}>
            <Loader2 size={32} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
            <p>Loading campaigns…</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && campaigns.length === 0 && (
          <div style={{
            textAlign: 'center', padding: 'var(--space-16)',
            background: 'white', borderRadius: 'var(--radius-2xl)',
            border: '1px solid var(--color-gray-100)',
          }}>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-4)' }}>📋</div>
            <h3 style={{ color: 'var(--color-navy)', marginBottom: 'var(--space-2)' }}>No campaigns yet</h3>
            <p style={{ color: 'var(--color-gray-500)', marginBottom: 'var(--space-6)' }}>
              Create your first campaign to get started.
            </p>
            <button className="btn btn-primary" onClick={openCreate}>
              <Plus size={16} /> Create Campaign
            </button>
          </div>
        )}

        {/* Campaigns table */}
        {!loading && campaigns.length > 0 && (
          <div style={{
            background: 'white', borderRadius: 'var(--radius-2xl)',
            border: '1px solid var(--color-gray-100)', overflow: 'hidden',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--color-gray-50)', borderBottom: '1px solid var(--color-gray-200)' }}>
                  {['Name', 'Status', 'Start', 'End', 'Created', 'Actions'].map(h => (
                    <th key={h} style={{
                      padding: 'var(--space-3) var(--space-4)',
                      textAlign: 'left', fontSize: 'var(--text-xs)',
                      fontWeight: 600, color: 'var(--color-gray-500)',
                      textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {campaigns.map((c, i) => (
                  <tr key={c.id} style={{
                    borderBottom: i < campaigns.length - 1 ? '1px solid var(--color-gray-100)' : 'none',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--color-gray-50)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}
                  >
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-navy)' }}>{c.name}</span>
                      {c.description && (
                        <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--text-xs)', marginTop: 2 }}>
                          {c.description.length > 60 ? c.description.slice(0, 60) + '…' : c.description}
                        </p>
                      )}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--color-gray-600)', fontSize: 'var(--text-sm)' }}>
                      {formatDate(c.start_at)}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--color-gray-600)', fontSize: 'var(--text-sm)' }}>
                      {formatDate(c.end_at)}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--color-gray-500)', fontSize: 'var(--text-xs)' }}>
                      {formatDate(c.created_at)}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                        <button
                          onClick={() => openEdit(c)}
                          className="btn btn-ghost btn-sm"
                          aria-label={`Edit ${c.name}`}
                          style={{ padding: '4px 8px' }}
                        >
                          <Pencil size={14} />
                        </button>
                        <button
                          onClick={() => confirmDelete(c.id)}
                          className="btn btn-ghost btn-sm"
                          aria-label={`Delete ${c.name}`}
                          style={{ padding: '4px 8px', color: 'var(--color-error)' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* ── Create / Edit modal ──────────────────────────────────────── */}
      {showForm && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, padding: 'var(--space-4)',
        }} onClick={e => e.target === e.currentTarget && closeForm()}>
          <div style={{
            background: 'white', borderRadius: 'var(--radius-2xl)',
            padding: 'var(--space-8)', width: '100%', maxWidth: 520,
            boxShadow: 'var(--shadow-2xl)',
          }}>
            <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, color: 'var(--color-navy)', marginBottom: 'var(--space-6)' }}>
              {editId ? 'Edit Campaign' : 'New Campaign'}
            </h2>

            {formError && (
              <div role="alert" style={{
                background: 'var(--color-error-bg)', color: 'var(--color-error)',
                border: '1px solid var(--color-error)', borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-3)', marginBottom: 'var(--space-4)',
                fontSize: 'var(--text-sm)', display: 'flex', gap: 8,
              }}>
                <AlertCircle size={15} style={{ flexShrink: 0 }} /> {formError}
              </div>
            )}

            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div className="form-group">
                <label htmlFor="camp-name" className="form-label">Campaign Name *</label>
                <input id="camp-name" name="name" type="text"
                  className="form-input" placeholder="e.g. Summer Newsletter"
                  value={form.name} onChange={handleFormChange}
                  disabled={saving} autoFocus />
              </div>
              <div className="form-group">
                <label htmlFor="camp-desc" className="form-label">Description</label>
                <textarea id="camp-desc" name="description"
                  className="form-input" placeholder="Optional description…"
                  value={form.description} onChange={handleFormChange}
                  disabled={saving} rows={3}
                  style={{ resize: 'vertical' }} />
              </div>
              <div className="form-group">
                <label htmlFor="camp-status" className="form-label">Status</label>
                <select id="camp-status" name="status"
                  className="form-input" value={form.status}
                  onChange={handleFormChange} disabled={saving}>
                  {STATUS_OPTIONS.map(s => (
                    <option key={s} value={s} style={{ textTransform: 'capitalize' }}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <div className="form-group">
                  <label htmlFor="camp-start" className="form-label">Start Date</label>
                  <input id="camp-start" name="start_at" type="datetime-local"
                    className="form-input" value={form.start_at}
                    onChange={handleFormChange} disabled={saving} />
                </div>
                <div className="form-group">
                  <label htmlFor="camp-end" className="form-label">End Date</label>
                  <input id="camp-end" name="end_at" type="datetime-local"
                    className="form-input" value={form.end_at}
                    onChange={handleFormChange} disabled={saving} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end', marginTop: 'var(--space-2)' }}>
                <button type="button" className="btn btn-ghost" onClick={closeForm} disabled={saving}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite', marginRight: 6 }} /> Saving…</> : (editId ? 'Save Changes' : 'Create Campaign')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Delete confirmation modal ─────────────────────────────────── */}
      {deleteId && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, padding: 'var(--space-4)',
        }}>
          <div style={{
            background: 'white', borderRadius: 'var(--radius-2xl)',
            padding: 'var(--space-8)', width: '100%', maxWidth: 400,
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '2rem', marginBottom: 'var(--space-4)' }}>🗑️</div>
            <h3 style={{ color: 'var(--color-navy)', marginBottom: 'var(--space-2)' }}>Delete Campaign?</h3>
            <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
              This action cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'center' }}>
              <button className="btn btn-ghost" onClick={cancelDelete} disabled={deleting}>Cancel</button>
              <button
                className="btn btn-primary"
                onClick={handleDelete}
                disabled={deleting}
                style={{ background: 'var(--color-error)', borderColor: 'var(--color-error)' }}
              >
                {deleting ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast notification ───────────────────────────────────────── */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, right: 24,
          background: 'var(--color-navy)', color: 'white',
          padding: 'var(--space-3) var(--space-5)', borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-xl)', display: 'flex', alignItems: 'center', gap: 8,
          fontSize: 'var(--text-sm)', fontWeight: 500, zIndex: 2000,
        }}>
          <CheckCircle size={16} color="var(--color-success)" />
          {toast}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
