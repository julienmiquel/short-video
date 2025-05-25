import React, { useEffect, useState } from 'react'; // Added useEffect, useState
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import CreateClipPage from './pages/CreateClipPage';
import GenerateHighlightsPage from './pages/GenerateHighlightsPage';
import { getCurrentUser, UserResponseData } from './services/apiService'; // Import getCurrentUser
import './App.css';

function App() {
  const [userEmail, setUserEmail] = useState<string | undefined>(undefined);
  const [authError, setAuthError] = useState<string | null>(null); // Optional: to display auth errors

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData: UserResponseData = await getCurrentUser();
        if (userData.email) {
          setUserEmail(userData.email);
        } else {
          // This case might occur if IAP_VALIDATION_ENABLED=false on backend,
          // or if the /me endpoint returns email: null for some reason.
          console.log("User email not available from /api/me");
          // setUserEmail(undefined); // already default
        }
      } catch (error) {
        console.error("Failed to fetch user:", error);
        setAuthError((error as Error).message); 
        // Decide if you want to show this error prominently.
        // For now, just log, as IAP should handle primary auth denial.
      }
    };

    fetchUser();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <Router>
      <div className="App">
        <Header userEmail={userEmail} /> {/* Pass userEmail to Header */}
        <main className="App-content">
          {/* Optional: Display auth error if needed 
          {authError && <p style={{color: 'red'}}>Auth Error: {authError}</p>} 
          */}
          <Routes>
            <Route path="/" element={<CreateClipPage />} />
            <Route path="/highlights" element={<GenerateHighlightsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
