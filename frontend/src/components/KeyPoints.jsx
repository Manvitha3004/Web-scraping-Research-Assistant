import './KeyPoints.css';

export function KeyPoints({ points }) {
  return (
    <div className="key-points-container">
      <h2 className="section-title">Key Points</h2>
      <ul className="key-points-list">
        {points.map((point, index) => (
          <li key={index} className="point-item">
            <span className="point-number">{index + 1}</span>
            <span className="point-text">{point}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
