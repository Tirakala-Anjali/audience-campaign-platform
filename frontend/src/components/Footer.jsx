import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

export default function Footer() {
  const year = new Date().getFullYear();

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <footer className="footer" role="contentinfo">
      <div className="container">
        <div className="footer-top">
          {/* Brand column */}
          <div>
            <Link to="/" className="footer-brand-logo" aria-label="AudienceFlow home">
              <div className="navbar-logo-icon" aria-hidden="true">
                <Activity size={20} color="white" strokeWidth={2.5} />
              </div>
              <span className="footer-brand-name">AudienceFlow</span>
            </Link>
            <p className="footer-brand-desc">
              Understand Your Audience. Create Smarter Campaigns. Build Stronger Connections.
            </p>
          </div>

          {/* Platform links */}
          <div>
            <p className="footer-col-title">Platform</p>
            <ul className="footer-links" role="list">
              <li>
                <button
                  onClick={() => scrollTo('features')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.45)', fontSize: 'var(--text-sm)', fontFamily: 'inherit', padding: 0, transition: 'color 200ms ease' }}
                  onMouseEnter={(e) => (e.target.style.color = 'rgba(255,255,255,0.85)')}
                  onMouseLeave={(e) => (e.target.style.color = 'rgba(255,255,255,0.45)')}
                >
                  Features
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollTo('how-it-works')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.45)', fontSize: 'var(--text-sm)', fontFamily: 'inherit', padding: 0, transition: 'color 200ms ease' }}
                  onMouseEnter={(e) => (e.target.style.color = 'rgba(255,255,255,0.85)')}
                  onMouseLeave={(e) => (e.target.style.color = 'rgba(255,255,255,0.45)')}
                >
                  How It Works
                </button>
              </li>
              <li><Link to="/register">Get Started</Link></li>
            </ul>
          </div>

          {/* Account links */}
          <div>
            <p className="footer-col-title">Account</p>
            <ul className="footer-links" role="list">
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Register</Link></li>
            </ul>
          </div>

          {/* Legal / Info */}
          <div>
            <p className="footer-col-title">Info</p>
            <ul className="footer-links" role="list">
              <li><span style={{ color: 'rgba(255,255,255,0.45)', fontSize: 'var(--text-sm)' }}>Milestone 1 — Demo</span></li>
              <li><span style={{ color: 'rgba(255,255,255,0.45)', fontSize: 'var(--text-sm)' }}>College Project</span></li>
              <li>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  API Docs ↗
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="footer-bottom">
          <p className="footer-copy">
            &copy; {year} AudienceFlow. All rights reserved.
          </p>
          <p className="footer-tagline">
            &ldquo;Understand Your Audience. Create Smarter Campaigns.&rdquo;
          </p>
        </div>
      </div>
    </footer>
  );
}
