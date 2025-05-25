// Define interfaces for API requests and responses based on backend models

export interface ClipRequestPayload {
  youtube_url: string;
  start_time: number;
  duration: number;
  clip_name?: string; // Optional
}

export interface ClipResponseData { // Matches backend ClipResponse
  clip_path: string | null;
  message: string | null;
  highlights: { highlights: { timestamp: string; reasoning: string }[] } | null;
}

export interface ErrorResponse { // Common error structure from FastAPI
     detail?: string | { msg: string, type: string, loc: (string|number)[] }[]; // Pydantic errors can be more complex
     error?: string; // Custom error from our 500 handler
}


const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api'; // Proxy will handle this in dev

export const createClip = async (payload: ClipRequestPayload): Promise<ClipResponseData> => {
  const response = await fetch(`${API_BASE_URL}/create_clip`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData: ErrorResponse = await response.json().catch(() => ({ detail: 'Unknown error structure' }));
    // Construct a meaningful error message
    let errorMessage = `API Error: ${response.status}`;
    if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
    } else if (Array.isArray(errorData.detail)) { // Pydantic validation error
        errorMessage = errorData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('; ');
    } else if (errorData.error && errorData.detail) { // Custom 500 error
         errorMessage = `${errorData.error}: ${errorData.detail}`;
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<ClipResponseData>;
};

// Added for User Authentication feature
export interface UserResponseData { // Matches backend UserResponse
  email: string | null;
}

export const getCurrentUser = async (): Promise<UserResponseData> => {
  // API_BASE_URL is '/api', so this becomes '/api/me'
  const response = await fetch(`${API_BASE_URL}/me`, { 
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // IAP authentication is handled by the browser sending cookies or IAP injecting headers.
      // No explicit 'Authorization' header needed from client to backend if IAP is set up.
    },
  });

  if (!response.ok) {
    // If IAP is enabled and user is not authenticated, IAP itself might block
    // or the /me endpoint would return 401 if it reaches the app without valid IAP state.
    const errorData: ErrorResponse = await response.json().catch(() => ({ detail: 'Failed to fetch user' }));
    let errorMessage = `API Error: ${response.status}`;
     if (typeof errorData.detail === 'string') {
         errorMessage = errorData.detail;
     } else if (errorData.error && errorData.detail) { // Matches the backend's 500 error structure for /api/me
         errorMessage = `${errorData.error}: ${errorData.detail}`;
     } else if (Array.isArray(errorData.detail)) { // Pydantic validation error (less likely for GET /me)
        errorMessage = errorData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('; ');
     }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<UserResponseData>;
};

// Added for Generate Highlights feature
export interface GenerateHighlightsPayload {
  youtube_url: string;
}

// Assuming ClipResponseData is suitable for generate_highlights response.
// The backend's /generate_highlights endpoint returns a ClipResponse model,
// where clip_path will be null, and message and highlights will be populated.
export const generateHighlights = async (payload: GenerateHighlightsPayload): Promise<ClipResponseData> => {
  const response = await fetch(`${API_BASE_URL}/generate_highlights`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData: ErrorResponse = await response.json().catch(() => ({ detail: 'Unknown error structure' }));
    let errorMessage = `API Error: ${response.status}`;
    if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
    } else if (Array.isArray(errorData.detail)) { // Pydantic validation error
        errorMessage = errorData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('; ');
    } else if (errorData.error && errorData.detail) { // Custom 500 error
         errorMessage = `${errorData.error}: ${errorData.detail}`;
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<ClipResponseData>;
};
