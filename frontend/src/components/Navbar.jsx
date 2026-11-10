import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const navigate = useNavigate();

  // Sync logged-in state when storage changes (e.g. login in another tab)
  useEffect(() => {
    const sync = () => setIsLoggedIn(!!localStorage.getItem('access_token'));
    window.addEventListener('storage', sync);
    // Also re-check on every mount
    sync();
    return () => window.removeEventListener('storage', sync);
  }, []);

  // Detect scroll to apply backdrop-blur style
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close mobile menu on resize to desktop
  useEffect(() => {
    const onResize = () => { if (window.innerWidth > 768) setMenuOpen(false); };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  // Smooth-scroll to a section id
  const scrollTo = (id) => {
    setMenuOpen(false);
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    } else {
      // If we're not on the landing page, navigate there first then scroll
      navigate('/');
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  return (
    <>
      <nav className={`navbar${scrolled ? ' scrolled' : ''}`} role="navigation" aria-label="Main navigation">
        <div className="navbar-inner">
          {/* Logo */}
          <Link to="/" className="navbar-logo" aria-label="AudienceFlow home">
            <div className="navbar-logo-icon" aria-hidden="true">
              <Activity size={22} color="white" strokeWidth={2.5} />
            </div>
            <span className="navbar-logo-text">AudienceFlow</span>
          </Link>

          {/* Desktop nav links */}
          <ul className="navbar-links" role="list">
            <li>
              <Link to="/" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                Home
              </Link>
            </li>
            <li>
              <button
                onClick={() => scrollTo('features')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.8)', fontWeight: 500, fontSize: 'var(--text-sm)', padding: 0, fontFamily: 'inherit' }}
              >
                Features
              </button>
            </li>
            <li>
              <button
                onClick={() => scrollTo('how-it-works')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.8)', fontWeight: 500, fontSize: 'var(--text-sm)', padding: 0, fontFamily: 'inherit' }}
              >
                How It Works
              </button>
            </li>
          </ul>

          {/* Desktop action buttons */}
          <div className="navbar-actions">
            {isLoggedIn ? (
              <>
                <Link to="/dashboard" className="btn btn-outline-white btn-sm">
                  <LayoutDashboard size={14} aria-hidden="true" /> Dashboard
                </Link>
                <Link to="/campaigns" className="btn btn-primary btn-sm">
                  Campaigns
                </Link>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline-white btn-sm">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Hamburger (mobile only) */}
          <button
            className={`navbar-hamburger${menuOpen ? ' open' : ''}`}
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      <div
        id="mobile-menu"
        className={`navbar-mobile${menuOpen ? ' open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <Link to="/" onClick={() => setMenuOpen(false)}>Home</Link>
        <button
          onClick={() => scrollTo('features')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.85)', fontWeight: 500, fontSize: 'var(--text-base)', padding: 'var(--space-2) 0', borderBottom: '1px solid rgba(255,255,255,0.06)', textAlign: 'left', fontFamily: 'inherit' }}
        >
          Features
        </button>
        <button
          onClick={() => scrollTo('how-it-works')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.85)', fontWeight: 500, fontSize: 'var(--text-base)', padding: 'var(--space-2) 0', borderBottom: '1px solid rgba(255,255,255,0.06)', textAlign: 'left', fontFamily: 'inherit' }}
        >
          How It Works
        </button>
        <div className="navbar-mobile-actions">
          {isLoggedIn ? (
            <>
              <Link to="/dashboard" className="btn btn-outline-white" onClick={() => setMenuOpen(false)}>
                <LayoutDashboard size={14} /> Dashboard
              </Link>
              <Link to="/campaigns" className="btn btn-primary" onClick={() => setMenuOpen(false)}>
                Campaigns
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline-white" onClick={() => setMenuOpen(false)}>
                Login
              </Link>
              <Link to="/register" className="btn btn-primary" onClick={() => setMenuOpen(false)}>
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </>
  );
}
