/**
 * FeatureCard
 *
 * Props:
 *   icon        — Lucide React component (e.g. <Languages />)
 *   title       — Feature name string
 *   description — Short description string
 *   delay       — Optional animation delay in ms (for staggered entrance)
 */
export default function FeatureCard({ icon: Icon, title, description, delay = 0 }) {
  return (
    <article
      className="feature-card card-hover"
      style={{ animationDelay: `${delay}ms` }}
      aria-label={`Feature: ${title}`}
    >
      <div className="feature-icon-wrap" aria-hidden="true">
        {Icon && <Icon size={26} strokeWidth={1.75} />}
      </div>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>
    </article>
  );
}
