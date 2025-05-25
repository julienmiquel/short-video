import React, { useState } from 'react';
import { createClip, ClipRequestPayload, ClipResponseData } from '../services/apiService';
import './CreateClipForm.css'; // We'll create this CSS file

const CreateClipForm: React.FC = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [startTime, setStartTime] = useState('');
  const [duration, setDuration] = useState('');
  const [clipName, setClipName] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clipResult, setClipResult] = useState<ClipResponseData | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setClipResult(null);
    setIsLoading(true);

    if (!youtubeUrl || !startTime || !duration) {
      setError("YouTube URL, Start Time, and Duration are required.");
      setIsLoading(false);
      return;
    }

    const payload: ClipRequestPayload = {
      youtube_url: youtubeUrl,
      start_time: parseInt(startTime, 10),
      duration: parseInt(duration, 10),
      ...(clipName && { clip_name: clipName }), // Add if clipName is not empty
    };

    try {
      const result = await createClip(payload);
      setClipResult(result);
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
    <div className="create-clip-form-container">
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="youtubeUrl">YouTube URL:</label>
          <input
            type="text"
            id="youtubeUrl"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="startTime">Start Time (seconds):</label>
          <input
            type="number"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="duration">Duration (seconds):</label>
          <input
            type="number"
            id="duration"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="clipName">Clip Name (optional):</label>
          <input
            type="text"
            id="clipName"
            value={clipName}
            onChange={(e) => setClipName(e.target.value)}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating Clip...' : 'Create Clip'}
        </button>
      </form>

      {error && <p className="error-message">Error: {error}</p>}
      
      {clipResult && clipResult.clip_path && (
        <div className="clip-result">
          <h3>Clip Created!</h3>
          <p>Path: {clipResult.clip_path}</p>
          {/* We will add a video player or download link here later */}
          <video width="320" height="240" controls key={clipResult.clip_path}>
            {/* This assumes the clip_path is directly accessible. 
                For Cloud Run, clips are typically stored in a bucket and served via signed URLs,
                or the backend needs an endpoint to serve them.
                For now, this will likely not play unless backend serves the file directly from 'clips/...' path.
            */}
            <source src={clipResult.clip_path} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}
      {clipResult && !clipResult.clip_path && clipResult.message && (
         <p>Message: {clipResult.message}</p>
      )}
    </div>
  );
};

export default CreateClipForm;
