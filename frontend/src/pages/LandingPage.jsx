import { Link } from 'react-router-dom';
import {
  Languages,
  Sparkles,
  Share2,
  BarChart3,
  ArrowRight,
  ChevronDown,
} from 'lucide-react';
import FeatureCard from '../components/FeatureCard';
import StepCard from '../components/StepCard';
import '../styles/landing.css';

// ---------------------------------------------------------------------------
// Static data
// ---------------------------------------------------------------------------

const FEATURES = [
  {
    icon: Languages,
    title: 'Multilingual Communication',
    description:
      'Communicate with your audience in their preferred languages to increase engagement and build trust across diverse communities.',
  },
  {
    icon: Sparkles,
    title: 'AI-Powered Content',
    description:
      'Prepare personalised campaign content using future AI integrations — smart suggestions tailored to each audience segment.',
  },
  {
    icon: Share2,
    title: 'Multi-Channel Campaigns',
    description:
      'Plan and coordinate communication across email, SMS, push notifications, and other supported channels from a single platform.',
  },
  {
    icon: BarChart3,
    title: 'Analytics & Insights',
    description:
      'Understand delivery performance, open rates, engagement metrics, and campaign results to continuously optimise your strategy.',
  },
];

const STEPS = [
  {
    title: 'Add Audience Members',
    description: 'Import or manually add contacts with their details, language preferences, and consent status.',
  },
  {
    title: 'Create Audience Segments',
    description: 'Group your audience with flexible filter criteria to target the right people every time.',
  },
  {
    title: 'Plan Campaigns',
    description: 'Define your campaign objectives, schedule, and target segments for a coordinated outreach.',
  },
  {
    title: 'Select Templates & Channels',
    description: 'Choose from multilingual message templates and pick the best communication channels for your goals.',
  },
  {
    title: 'Monitor Performance',
    description: 'Track delivery, engagement, and audience feedback in real time to measure and improve results.',
  },
];

// ---------------------------------------------------------------------------
// Dashboard preview SVG mockup (inline, no external asset needed)
// ---------------------------------------------------------------------------

function DashboardPreview() {
  const bars = [45, 65, 50, 80, 60, 90, 72, 85, 55, 95, 70, 88];
  const colors = [
    '#7C3AED','#9B67F0','#7C3AED','#A78BFA',
    '#06B6D4','#7C3AED','#9B67F0','#A78BFA',
    '#7C3AED','#06B6D4','#9B67F0','#7C3AED',
  ];

  return (
    <div className="hero-dashboard" role="img" aria-label="AudienceFlow dashboard preview">
      {/* Window chrome */}
      <div className="dashboard-header">
        <span className="dashboard-title">Campaign Overview</span>
        <div className="dashboard-dots">
          <div className="dashboard-dot" style={{ background: '#EF4444' }} />
          <div className="dashboard-dot" style={{ background: '#F59E0B' }} />
          <div className="dashboard-dot" style={{ background: '#10B981' }} />
        </div>
      </div>

      {/* Metric cards */}
      <div className="dashboard-metrics">
        <div className="metric-card">
          <div className="metric-label">Audience</div>
          <div className="metric-value">12,480</div>
          <div className="metric-delta up">↑ 8.2%</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Campaigns</div>
          <div className="metric-value">34</div>
          <div className="metric-delta up">↑ 3 new</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Open Rate</div>
          <div className="metric-value">68%</div>
          <div className="metric-delta up">↑ 4.1%</div>
        </div>
      </div>

      {/* Bar chart */}
      <div className="dashboard-chart" aria-hidden="true">
        {bars.map((h, i) => (
          <div
            key={i}
            className="chart-bar"
            style={{
              height: `${h}%`,
              background: `linear-gradient(to top, ${colors[i]}, ${colors[i]}99)`,
            }}
          />
        ))}
      </div>

      {/* Campaign rows */}
      <div className="dashboard-campaigns">
        {[
          { name: 'Summer Newsletter', status: 'active',  label: 'Active'  },
          { name: 'Onboarding Series',  status: 'active',  label: 'Active'  },
          { name: 'Re-engagement Q4',   status: 'draft',   label: 'Draft'   },
          { name: 'Product Launch',     status: 'paused',  label: 'Paused'  },
        ].map((c) => (
          <div key={c.name} className="campaign-row">
            <span className="campaign-name">{c.name}</span>
            <span className={`campaign-status status-${c.status}`}>{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function LandingPage({ apiStatus }) {
  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      {/* ── Hero ──────────────────────────────────────────────── */}
      <section className="hero" aria-labelledby="hero-title">
        <div className="container">
          <div className="hero-inner">
            {/* Left: copy */}
            <div className="hero-content">
              <div className="hero-eyebrow">
                <span className="hero-eyebrow-dot" aria-hidden="true" />
                Audience Management Platform
              </div>

              <h1 className="hero-title" id="hero-title">
                Smarter Campaigns,{' '}
                <span className="hero-title-highlight">Stronger Connections</span>
              </h1>

              <p className="hero-description">
                Understand your audience, craft personalised multi-channel campaigns, and
                measure real impact — all from a single, powerful platform built for modern teams.
              </p>

              <div className="hero-actions">
                <Link to="/register" className="btn btn-primary btn-lg">
                  Get Started Free
                  <ArrowRight size={18} aria-hidden="true" />
                </Link>
                <button
                  className="btn btn-outline-white btn-lg"
                  onClick={scrollToFeatures}
                  aria-label="Scroll to features section"
                >
                  Explore Features
                  <ChevronDown size={18} aria-hidden="true" />
                </button>
              </div>

              {/* Stats row */}
              <div className="hero-stats" aria-label="Platform statistics">
                <div className="hero-stat">
                  <span className="hero-stat-value">9</span>
                  <span className="hero-stat-label">Core Tables</span>
                </div>
                <div className="hero-stat">
                  <span className="hero-stat-value">5</span>
                  <span className="hero-stat-label">Workflow Steps</span>
                </div>
                <div className="hero-stat">
                  <span className="hero-stat-value">4</span>
                  <span className="hero-stat-label">Channels</span>
                </div>
              </div>

              {/* API connectivity badge */}
              {apiStatus && (
                <div
                  className={`api-status ${apiStatus.state}`}
                  aria-live="polite"
                  aria-label={`Backend API status: ${apiStatus.label}`}
                >
                  <span className="api-status-dot" aria-hidden="true" />
                  {apiStatus.label}
                </div>
              )}
            </div>

            {/* Right: dashboard preview */}
            <div className="hero-visual">
              <DashboardPreview />
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────── */}
      <section id="features" className="features section" aria-labelledby="features-title">
        <div className="container">
          <header className="section-header">
            <span className="section-eyebrow">Platform Features</span>
            <h2 className="section-title" id="features-title">
              Everything You Need to Connect with Your Audience
            </h2>
            <p className="section-subtitle">
              A complete toolkit for audience management, campaign planning, and performance tracking —
              designed to grow with your needs.
            </p>
          </header>

          <div className="features-grid">
            {FEATURES.map((f, i) => (
              <FeatureCard
                key={f.title}
                icon={f.icon}
                title={f.title}
                description={f.description}
                delay={i * 100}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────── */}
      <section id="how-it-works" className="how-it-works section" aria-labelledby="how-title">
        <div className="container">
          <header className="section-header">
            <span className="section-eyebrow">How It Works</span>
            <h2 className="section-title" id="how-title">
              From Audience to Campaign in Five Steps
            </h2>
            <p className="section-subtitle">
              AudienceFlow guides you through a clear, structured workflow from building your
              audience to measuring campaign performance.
            </p>
          </header>

          <div className="steps-grid">
            {STEPS.map((s, i) => (
              <StepCard
                key={s.title}
                step={i + 1}
                title={s.title}
                description={s.description}
                delay={i * 100}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────── */}
      <section className="cta-section" aria-labelledby="cta-title">
        <div className="container">
          <div className="cta-inner">
            <h2 className="cta-title" id="cta-title">
              Ready to Build Stronger Connections?
            </h2>
            <p className="cta-subtitle">
              Join AudienceFlow and start planning smarter campaigns that truly resonate
              with your audience — in their language, on their preferred channel.
            </p>
            <div className="cta-actions">
              <Link to="/register" className="btn btn-primary btn-lg">
                Start Planning Smarter Campaigns
                <ArrowRight size={18} aria-hidden="true" />
              </Link>
              <Link to="/login" className="btn btn-outline-white btn-lg">
                Sign In
              </Link>
            </div>
            <p className="cta-note">No credit card required &bull; College project demo</p>
          </div>
        </div>
      </section>
    </>
  );
}
