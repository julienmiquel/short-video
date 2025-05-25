import React from 'react';
import GenerateHighlightsForm from '../components/GenerateHighlightsForm'; // Import the form

const GenerateHighlightsPage: React.FC = () => {
  return (
    <div>
      <h2>Generate Video Highlights</h2>
      <GenerateHighlightsForm /> {/* Use the form component */}
    </div>
  );
};

export default GenerateHighlightsPage;
