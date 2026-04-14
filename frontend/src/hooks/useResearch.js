import { useState, useCallback } from 'react';

const API_BASE_URL = '/api';

export function useResearch() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const performResearch = useCallback(async (query, numSources = 5) => {
    setLoading(true);
    setError(null);
    setProgress(0);

    try {
      // Step 1: Searching
      setProgress(25);

      const response = await fetch(`${API_BASE_URL}/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          num_sources: numSources,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Step 2: Scraping
      setProgress(50);

      // Step 3: Analyzing
      setProgress(75);

      const result = await response.json();

      // Step 4: Summarizing
      setProgress(100);

      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      console.error('Research error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearData = useCallback(() => {
    setData(null);
    setError(null);
    setProgress(0);
  }, []);

  return {
    data,
    loading,
    error,
    progress,
    performResearch,
    clearData,
  };
}
