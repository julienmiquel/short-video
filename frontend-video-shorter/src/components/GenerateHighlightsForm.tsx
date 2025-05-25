import React, { useState } from 'react';
import { generateHighlights, GenerateHighlightsPayload, ClipResponseData } from '../services/apiService';
import './GenerateHighlightsForm.css'; // We'll create this CSS file

const GenerateHighlightsForm: React.FC = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightsResult, setHighlightsResult] = useState<ClipResponseData | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setHighlightsResult(null);
    setIsLoading(true);

    if (!youtubeUrl) {
      setError("YouTube URL is required.");
      setIsLoading(false);
      return;
    }

    const payload: GenerateHighlightsPayload = {
      youtube_url: youtubeUrl,
    };

    try {
      const result = await generateHighlights(payload);
      setHighlightsResult(result);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="generate-highlights-form-container">
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="youtubeUrlHighlights">YouTube URL:</label>
          <input
            type="text"
            id="youtubeUrlHighlights"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generating Highlights...' : 'Generate Highlights'}
        </button>
      </form>

      {error && <p className="error-message">Error: {error}</p>}
      
      {highlightsResult && (
        <div className="highlights-result">
          <h3>{highlightsResult.message || "Highlights Generated"}</h3>
          {highlightsResult.highlights && highlightsResult.highlights.highlights.length > 0 ? (
            <ul>
              {highlightsResult.highlights.highlights.map((highlight, index) => (
                <li key={index}>
                  <strong>Timestamp:</strong> {highlight.timestamp} <br />
                  <strong>Reasoning:</strong> {highlight.reasoning}
                </li>
              ))}
            </ul>
          ) : (
            <p>No specific highlight details returned, or no highlights found.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default GenerateHighlightsForm;
