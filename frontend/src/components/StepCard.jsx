/**
 * StepCard
 *
 * Props:
 *   step        — Step number (integer)
 *   title       — Step name string
 *   description — Short explanation string
 *   delay       — Optional animation delay in ms
 */
export default function StepCard({ step, title, description, delay = 0 }) {
  return (
    <article
      className="step-card"
      style={{ animationDelay: `${delay}ms` }}
      aria-label={`Step ${step}: ${title}`}
    >
      <div className="step-number" aria-hidden="true">
        {step}
      </div>
      <div className="step-content">
        <h3 className="step-title">{title}</h3>
        <p className="step-description">{description}</p>
      </div>
    </article>
  );
}
