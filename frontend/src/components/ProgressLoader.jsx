import './ProgressLoader.css';

const STEPS = [
  { label: 'Searching', percent: 25 },
  { label: 'Scraping', percent: 50 },
  { label: 'Analyzing', percent: 75 },
  { label: 'Summarizing', percent: 100 },
];

export function ProgressLoader({ progress }) {
  return (
    <div className="progress-container">
      <div className="progress-bar-wrapper">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
      </div>
      
      <div className="steps-container">
        {STEPS.map((step, index) => (
          <div key={step.label} className={`step ${progress >= step.percent ? 'active' : ''}`}>
            <div className="step-number">{index + 1}</div>
            <div className="step-label">{step.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
