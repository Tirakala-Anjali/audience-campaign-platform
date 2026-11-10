/**
 * DashboardPage — AudienceFlow
 *
 * Shows role-specific statistics:
 *   Campaign Manager / Admin → campaign-focused cards + status breakdown
 *   Communication Team       → audience & message-focused cards
 *
 * Both views share the Recent Campaigns section and the same header/nav.
 */
import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity, BarChart3, Users, Megaphone, FileText,
  CheckCircle2, PauseCircle, XCircle, RefreshCw,
  Loader2, AlertCircle, LogOut, LayoutDashboard,
  TrendingUp, ArrowRight, MessageSquare, UserCheck,
  Send, Inbox,
} from 'lucide-react';
import { getDashboardStats, getMe, logout } from '../services/api';
import '../styles/global.css';

// ─── Status colours ───────────────────────────────────────────────────────────

const STATUS_META = {
  active:    { color: '#10B981', bg: '#D1FAE5', icon: TrendingUp  },
  draft:     { color: '#6B7280', bg: '#F3F4F6', icon: FileText    },
  paused:    { color: '#F59E0B', bg: '#FEF3C7', icon: PauseCircle },
  completed: { color: '#3B82F6', bg: '#DBEAFE', icon: CheckCircle2 },
  cancelled: { color: '#EF4444', bg: '#FEE2E2', icon: XCircle     },
};

function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

// ─── Reusable stat card ───────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, accent, sub, note }) {
  return (
    <div
      style={{
        background: 'white', borderRadius: 'var(--radius-2xl)',
        padding: 'var(--space-6)', border: '1px solid var(--color-gray-100)',
        boxShadow: 'var(--shadow-sm)', display: 'flex', flexDirection: 'column',
        gap: 'var(--space-3)', transition: 'box-shadow 0.2s ease',
      }}
      onMouseEnter={e => (e.currentTarget.style.boxShadow = 'var(--shadow-lg)')}
      onMouseLeave={e => (e.currentTarget.style.boxShadow = 'var(--shadow-sm)')}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 'var(--radius-xl)',
        background: accent + '20', display: 'flex',
        alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={22} color={accent} />
      </div>
      <div>
        <div style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: 'var(--color-navy)', lineHeight: 1 }}>
          {value}
        </div>
        <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-gray-500)', marginTop: 4 }}>
          {label}
        </div>
        {sub && (
          <div style={{ fontSize: 'var(--text-xs)', color: accent, marginTop: 2, fontWeight: 600 }}>
            {sub}
          </div>
        )}
        {note && (
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-gray-400)', marginTop: 2 }}>
            {note}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Role badge ───────────────────────────────────────────────────────────────

const ROLE_META = {
  'Campaign Manager':   { color: '#7C3AED', bg: '#EDE9FE', label: 'Campaign Manager' },
  'Communication Team': { color: '#0891B2', bg: '#CFFAFE', label: 'Communication Team' },
  'Admin':              { color: '#DC2626', bg: '#FEE2E2', label: 'Admin' },
};

function RoleBadge({ role }) {
  const m = ROLE_META[role] || { color: '#6B7280', bg: '#F3F4F6', label: role };
  return (
    <span style={{
      background: m.bg, color: m.color,
      padding: '3px 10px', borderRadius: 999,
      fontSize: 'var(--text-xs)', fontWeight: 700,
      textTransform: 'uppercase', letterSpacing: '0.04em',
    }}>
      {m.label}
    </span>
  );
}

// ─── Campaign Manager stats cards ────────────────────────────────────────────

function CampaignManagerStats({ stats }) {
  const total = stats.total_campaigns;
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: 'var(--space-5)',
      marginBottom: 'var(--space-8)',
    }}>
      <StatCard icon={Megaphone}    label="Total Campaigns"     value={total}                       accent="var(--color-purple)" />
      <StatCard icon={TrendingUp}   label="Active Campaigns"    value={stats.active_campaigns}       accent="#10B981"
        sub={total > 0 ? `${Math.round((stats.active_campaigns / total) * 100)}% of total` : undefined} />
      <StatCard icon={FileText}     label="Draft Campaigns"     value={stats.draft_campaigns}        accent="#6B7280" />
      <StatCard icon={PauseCircle}  label="Paused"              value={stats.paused_campaigns}       accent="#F59E0B" />
      <StatCard icon={CheckCircle2} label="Completed"           value={stats.completed_campaigns}    accent="#3B82F6" />
      <StatCard icon={Users}        label="Registered Users"    value={stats.total_registered_users} accent="var(--color-navy)"
        note="Platform accounts" />
    </div>
  );
}

// ─── Communication Team stats cards ──────────────────────────────────────────

function CommunicationTeamStats({ stats }) {
  const consented = stats.consented_audience_members;
  const total     = stats.total_audience_members;
  const pct       = total > 0 ? Math.round((consented / total) * 100) : 0;
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: 'var(--space-5)',
      marginBottom: 'var(--space-8)',
    }}>
      <StatCard icon={Users}        label="Total Audience"      value={total}
        accent="#3B82F6"
        note={total === 0 ? 'No audience imported yet' : undefined} />
      <StatCard icon={UserCheck}    label="Consented Members"   value={consented}
        accent="#10B981"
        sub={total > 0 ? `${pct}% consent rate` : undefined}
        note={total === 0 ? 'No audience data yet' : undefined} />
      <StatCard icon={Send}         label="Messages Sent"       value={stats.total_messages_sent}
        accent="var(--color-purple)"
        note={stats.total_messages_sent === 0 ? 'No messages sent yet' : undefined} />
      <StatCard icon={Megaphone}    label="Active Campaigns"    value={stats.active_campaigns}
        accent="#F59E0B"
        sub={stats.active_campaigns > 0 ? 'Currently running' : undefined} />
      <StatCard icon={CheckCircle2} label="Completed Campaigns" value={stats.completed_campaigns}
        accent="#0891B2" />
      <StatCard icon={Users}        label="Registered Users"    value={stats.total_registered_users}
        accent="var(--color-navy)"
        note="Platform accounts" />
    </div>
  );
}

// ─── Status breakdown bar ────────────────────────────────────────────────────

function StatusBreakdown({ breakdown, total }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <div style={{
        background: 'white', borderRadius: 'var(--radius-2xl)',
        border: '1px solid var(--color-gray-100)', padding: 'var(--space-6)',
        boxShadow: 'var(--shadow-sm)', textAlign: 'center',
        color: 'var(--color-gray-400)', fontSize: 'var(--text-sm)',
      }}>
        No campaigns to display yet.
      </div>
    );
  }
  return (
    <div style={{
      background: 'white', borderRadius: 'var(--radius-2xl)',
      border: '1px solid var(--color-gray-100)', padding: 'var(--space-6)',
      boxShadow: 'var(--shadow-sm)',
    }}>
      <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--color-navy)', marginBottom: 'var(--space-5)' }}>
        Campaign Status Breakdown
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {breakdown.map(({ status, count }) => {
          const meta = STATUS_META[status] || { color: '#6B7280', bg: '#F3F4F6', icon: FileText };
          const pct  = total > 0 ? Math.round((count / total) * 100) : 0;
          const Icon = meta.icon;
          return (
            <div key={status}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <Icon size={14} color={meta.color} />
                  <span style={{ fontSize: 'var(--text-sm)', fontWeight: 600, textTransform: 'capitalize', color: 'var(--color-gray-700)' }}>
                    {status}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                  <span style={{ background: meta.bg, color: meta.color, padding: '1px 8px', borderRadius: 999, fontSize: 'var(--text-xs)', fontWeight: 600 }}>{count}</span>
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-gray-400)', minWidth: 30, textAlign: 'right' }}>{pct}%</span>
                </div>
              </div>
              <div style={{ height: 6, background: 'var(--color-gray-100)', borderRadius: 999 }}>
                <div style={{ height: '100%', borderRadius: 999, width: `${pct}%`, background: meta.color, transition: 'width 0.6s ease' }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Recent campaigns ────────────────────────────────────────────────────────

function RecentCampaigns({ campaigns }) {
  return (
    <div style={{
      background: 'white', borderRadius: 'var(--radius-2xl)',
      border: '1px solid var(--color-gray-100)', padding: 'var(--space-6)',
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-5)' }}>
        <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--color-navy)' }}>Recent Campaigns</h3>
        <Link to="/campaigns" style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--text-sm)', color: 'var(--color-purple)', fontWeight: 600, textDecoration: 'none' }}>
          View all <ArrowRight size={14} />
        </Link>
      </div>
      {campaigns.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--color-gray-400)' }}>
          <Megaphone size={28} style={{ marginBottom: 8, opacity: 0.4 }} />
          <p style={{ fontSize: 'var(--text-sm)' }}>
            No campaigns yet.{' '}
            <Link to="/campaigns" style={{ color: 'var(--color-purple)' }}>Create one →</Link>
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {campaigns.map((c, i) => {
            const meta = STATUS_META[c.status] || { color: '#6B7280', bg: '#F3F4F6' };
            return (
              <div key={c.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: 'var(--space-3) 0',
                borderBottom: i < campaigns.length - 1 ? '1px solid var(--color-gray-100)' : 'none',
              }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 600, color: 'var(--color-navy)', fontSize: 'var(--text-sm)', marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.name}</p>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-gray-400)' }}>Created {fmtDate(c.created_at)}</p>
                </div>
                <span style={{ background: meta.bg, color: meta.color, padding: '2px 10px', borderRadius: 999, fontSize: 'var(--text-xs)', fontWeight: 600, textTransform: 'capitalize', flexShrink: 0, marginLeft: 12 }}>
                  {c.status}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate  = useNavigate();
  const [user,    setUser]    = useState(null);
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { navigate('/login'); return; }
    getMe().then(setUser).catch(() => { localStorage.removeItem('access_token'); navigate('/login'); });
  }, [navigate]);

  const fetchStats = useCallback(async () => {
    setLoading(true); setError('');
    try {
      setStats(await getDashboardStats());
    } catch (err) {
      if (err.response?.status === 401) { localStorage.removeItem('access_token'); navigate('/login'); }
      else if (err.response?.status === 503) setError('Database is unavailable. Please try again.');
      else setError('Failed to load statistics. Please try again.');
    } finally { setLoading(false); }
  }, [navigate]);

  useEffect(() => { if (user) fetchStats(); }, [user, fetchStats]);

  const handleLogout = () => { logout(); navigate('/login'); };

  // Determine which role-view to show
  const role = stats?.user_role || user?.role || '';
  const isCommTeam = role === 'Communication Team';

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-off-white)' }}>

      {/* ── Header ──────────────────────────────────────────────────── */}
      <header style={{ background: 'var(--color-navy)', padding: 'var(--space-4) var(--space-8)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: 'linear-gradient(135deg, var(--color-purple), #06B6D4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Activity size={18} color="white" />
          </div>
          <span style={{ color: 'white', fontWeight: 700, fontSize: 'var(--text-lg)' }}>AudienceFlow</span>
        </Link>

        <nav style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
          <Link to="/dashboard" style={{ color: 'white', fontSize: 'var(--text-sm)', fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>
            <LayoutDashboard size={14} /> Dashboard
          </Link>
          <Link to="/campaigns" style={{ color: 'rgba(255,255,255,0.7)', fontSize: 'var(--text-sm)', textDecoration: 'none' }}>
            Campaigns
          </Link>
        </nav>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: 'var(--text-sm)' }}>{user.name}</span>
              <RoleBadge role={user.role} />
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.3)', color: 'white', cursor: 'pointer', borderRadius: 'var(--radius-lg)', padding: '6px 14px', fontSize: 'var(--text-sm)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'inherit', transition: 'background 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <LogOut size={14} /> Log out
          </button>
        </div>
      </header>

      {/* ── Body ─────────────────────────────────────────────────────── */}
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: 'var(--space-8)' }}>

        {/* Title row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-6)', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <div>
            <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: 'var(--color-navy)', margin: 0 }}>
              {isCommTeam ? 'Communications Dashboard' : 'Campaign Dashboard'}
            </h1>
            <p style={{ color: 'var(--color-gray-500)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
              {isCommTeam
                ? 'Audience reach, consent, and message activity'
                : 'Live campaign statistics from your database'}
            </p>
          </div>
          <button
            onClick={fetchStats} disabled={loading}
            style={{ background: 'white', border: '1px solid var(--color-gray-200)', color: 'var(--color-gray-700)', cursor: loading ? 'not-allowed' : 'pointer', borderRadius: 'var(--radius-lg)', padding: '8px 16px', fontSize: 'var(--text-sm)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'inherit', opacity: loading ? 0.6 : 1 }}
          >
            <RefreshCw size={14} style={loading ? { animation: 'spin 1s linear infinite' } : {}} />
            Refresh
          </button>
        </div>

        {/* Error */}
        {error && (
          <div role="alert" style={{ background: 'var(--color-error-bg)', border: '1px solid var(--color-error)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-6)', color: 'var(--color-error)', fontSize: 'var(--text-sm)' }}>
            <AlertCircle size={18} style={{ flexShrink: 0 }} /> <span>{error}</span>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && !stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-5)' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{ background: 'linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: 'var(--radius-2xl)', height: 130, border: '1px solid var(--color-gray-100)' }} />
            ))}
          </div>
        )}

        {/* Role-specific stat cards */}
        {stats && (
          <>
            {isCommTeam
              ? <CommunicationTeamStats stats={stats} />
              : <CampaignManagerStats   stats={stats} />
            }

            {/* Lower row — both roles see breakdown + recent */}
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(260px, 1fr) minmax(300px, 2fr)', gap: 'var(--space-5)' }}>
              <StatusBreakdown breakdown={stats.status_breakdown} total={stats.total_campaigns} />
              <RecentCampaigns campaigns={stats.recent_campaigns} />
            </div>
          </>
        )}

        {/* No campaigns yet */}
        {!loading && !error && stats && stats.total_campaigns === 0 && (
          <div style={{ textAlign: 'center', marginTop: 'var(--space-8)', padding: 'var(--space-8)', background: 'white', borderRadius: 'var(--radius-2xl)', border: '1px solid var(--color-gray-100)' }}>
            <Megaphone size={40} color="var(--color-gray-300)" style={{ marginBottom: 12 }} />
            <h3 style={{ color: 'var(--color-navy)' }}>No campaigns yet</h3>
            <p style={{ color: 'var(--color-gray-500)', marginBottom: 'var(--space-6)' }}>Create your first campaign to start seeing statistics here.</p>
            <Link to="/campaigns" className="btn btn-primary">Create your first campaign →</Link>
          </div>
        )}
      </main>

      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
      `}</style>
    </div>
  );
}
