import { useState, useEffect } from 'react';
import './SearchBar.css';

const EXAMPLE_QUERIES = [
  "What is artificial intelligence?",
  "Latest developments in renewable energy",
  "How does machine learning work?",
  "Impact of climate change on oceans",
  "Future of quantum computing"
];

export function SearchBar({ onSearch, loading, placeholder = "Search for a research topic..." }) {
  const [query, setQuery] = useState('');
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  // Typing animation for placeholder
  useEffect(() => {
    if (query) return; // Stop animation if user is typing

    const currentExample = EXAMPLE_QUERIES[currentIndex];
    let timeout;

    if (!isDeleting) {
      if (charIndex < currentExample.length) {
        timeout = setTimeout(() => {
          setDisplayText(currentExample.slice(0, charIndex + 1));
          setCharIndex(charIndex + 1);
        }, 50);
      } else {
        timeout = setTimeout(() => {
          setIsDeleting(true);
        }, 2000);
      }
    } else {
      if (charIndex > 0) {
        timeout = setTimeout(() => {
          setDisplayText(currentExample.slice(0, charIndex - 1));
          setCharIndex(charIndex - 1);
        }, 30);
      } else {
        setIsDeleting(false);
        setCurrentIndex((prev) => (prev + 1) % EXAMPLE_QUERIES.length);
      }
    }

    return () => clearTimeout(timeout);
  }, [charIndex, currentIndex, isDeleting, query]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query);
      setQuery('');
      setDisplayText('');
      setCharIndex(0);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          className="search-input"
          placeholder={displayText + (charIndex === EXAMPLE_QUERIES[currentIndex]?.length && !isDeleting ? '▌' : '')}
          value={query}
          onChange={handleInputChange}
          disabled={loading}
          autoFocus
        />
        <button 
          type="submit" 
          className="search-button"
          disabled={!query.trim() || loading}
        >
          {loading ? (
            <>
              <span className="loader"></span>
              Searching...
            </>
          ) : (
            <>
              Research
              <span className="icon">→</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
