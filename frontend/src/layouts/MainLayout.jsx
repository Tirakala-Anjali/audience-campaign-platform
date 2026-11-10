import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

/**
 * MainLayout
 * Wraps landing page content with the sticky Navbar and Footer.
 * Auth pages (Login/Register) use their own minimal layout.
 */
export default function MainLayout({ children }) {
  return (
    <>
      <Navbar />
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      <Footer />
    </>
  );
}
