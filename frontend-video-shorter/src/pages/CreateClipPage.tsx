import React from 'react';
import CreateClipForm from '../components/CreateClipForm'; // Import the form

const CreateClipPage: React.FC = () => {
  return (
    <div>
      <h2>Create Video Clip</h2>
      <CreateClipForm /> {/* Use the form component */}
    </div>
  );
};

export default CreateClipPage;
