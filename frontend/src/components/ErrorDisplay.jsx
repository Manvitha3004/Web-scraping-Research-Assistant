import './ErrorDisplay.css';

export function ErrorDisplay({ error, onRetry }) {
  return (
    <div className="error-container">
      <div className="error card">
        <div className="error-icon">⚠️</div>
        <div className="error-content">
          <h2>Research Failed</h2>
          <p>{error}</p>
          {onRetry && (
            <button className="retry-button" onClick={onRetry}>
              ↻ Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
