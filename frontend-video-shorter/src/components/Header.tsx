import React from 'react';
import { Link } from 'react-router-dom'; // Import Link
import './Header.css';

interface HeaderProps {
  userEmail?: string;
}

const Header: React.FC<HeaderProps> = ({ userEmail }) => {
  return (
    <header className="App-header">
      <h1>Video Shorter</h1>
      <nav>
        <Link to="/">Create Clip</Link> {/* Use Link */}
        <Link to="/highlights">Generate Highlights</Link> {/* Use Link */}
      </nav>
      {userEmail && <div className="user-info">Logged in as: {userEmail}</div>}
    </header>
  );
};

export default Header;
