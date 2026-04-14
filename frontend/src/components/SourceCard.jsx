import { useState } from 'react';
import './SourceCard.css';

export function SourceCard({ source, index }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getFavicon = (url) => {
    try {
      const domain = new URL(url).hostname;
      return `https://www.google.com/s2/favicons?sz=64&domain=${domain}`;
    } catch {
      return '📄';
    }
  };

  const truncateUrl = (url, maxLength = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
  };

  return (
    <div className="source-card-container">
      <div 
        className={`source-card ${isExpanded ? 'expanded' : ''}`}
        style={{ animationDelay: `${index * 0.1}s` }}
      >
        <div className="card-header">
          <div className="source-icon">
            <img 
              src={getFavicon(source.url)} 
              alt="favicon"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </div>
          <div className="source-info">
            <h3 className="source-title">{source.title}</h3>
            <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-url">
              {truncateUrl(source.url)}
            </a>
          </div>
          <button 
            className="expand-button"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>

        <div className="card-snippet">
          <p>{source.snippet.substring(0, 150)}...</p>
        </div>

        {isExpanded && source.scraped_content && (
          <div className="card-content">
            <div className="content-text">
              {source.scraped_content}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
