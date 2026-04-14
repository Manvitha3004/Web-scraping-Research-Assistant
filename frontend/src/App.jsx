import { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { ResearchReport } from './components/ResearchReport';
import { ProgressLoader } from './components/ProgressLoader';
import { ErrorDisplay } from './components/ErrorDisplay';
import { useResearch } from './hooks/useResearch';
import './styles/globals.css';
import './App.css';

function App() {
  const { data, loading, error, progress, performResearch, clearData } = useResearch();
  const [searchHistory, setSearchHistory] = useState([]);

  // Load search history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('searchHistory');
    if (saved) {
      try {
        setSearchHistory(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load search history:', e);
      }
    }
  }, []);

  // Save search history to localStorage
  const addToHistory = (query) => {
    const updated = [query, ...searchHistory.filter(q => q !== query)].slice(0, 5);
    setSearchHistory(updated);
    localStorage.setItem('searchHistory', JSON.stringify(updated));
  };

  const handleSearch = async (query) => {
    addToHistory(query);
    await performResearch(query);
  };

  const handleClearResults = () => {
    clearData();
  };

  const handleRetry = () => {
    if (data?.query) {
      handleSearch(data.query);
    }
  };

  return (
    <div className="app">
      {/* Hero Section */}
      <header className="hero-section">
        <div className="container">
          <div className="logo-section">
            <h1 className="main-title">
              <span className="title-icon">🔍</span>
              Research Assistant
            </h1>
            <p className="subtitle">
              AI-powered web research, scraping, and summarization
            </p>
          </div>

          <SearchBar 
            onSearch={handleSearch} 
            loading={loading}
            placeholder="Enter your research topic..."
          />

          {/* Search History */}
          {searchHistory.length > 0 && !data && (
            <div className="search-history">
              <p className="history-label">Recent Searches</p>
              <div className="history-chips">
                {searchHistory.map((query, index) => (
                  <button
                    key={index}
                    className="history-chip"
                    onClick={() => handleSearch(query)}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {loading && (
            <div className="loading-state">
              <ProgressLoader progress={progress} />
              <p className="loading-message">
                Performing autonomous research...
              </p>
            </div>
          )}

          {error && !loading && (
            <ErrorDisplay 
              error={error} 
              onRetry={handleRetry}
            />
          )}

          {data && !loading && (
            <div className="report-section">
              <ResearchReport data={data} />
              <div className="action-buttons">
                <button className="btn-secondary" onClick={handleClearResults}>
                  ← New Search
                </button>
              </div>
            </div>
          )}

          {!data && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">📚</div>
              <h2>Welcome to the Research Assistant</h2>
              <p>
                Enter a research topic above to start. The assistant will:
              </p>
              <ul className="features-list">
                <li>Search the web for relevant sources</li>
                <li>Scrape and extract content from those sources</li>
                <li>Analyze and summarize the findings</li>
                <li>Present a structured research report</li>
              </ul>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>
            <span className="footer-label">All using free APIs</span>
            <span className="footer-separator">•</span>
            <span>DuckDuckGo Search • Groq AI • BeautifulSoup</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
