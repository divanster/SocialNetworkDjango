// frontend/src/components/RightSidebar/RightSidebar.tsx

import React from 'react';
import FriendRequests from './FriendRequests';
import Birthdays from './Birthdays';
import Contacts from './Contacts';
import Suggestions from './Suggestions'; // Import Suggestions component
import './RightSidebar.css';

const RightSidebar: React.FC = () => {
  return (
    <div className="right-sidebar">
      <Suggestions /> {/* Add Suggestions here */}
      <FriendRequests />
      <Birthdays />
      <Contacts />
    </div>
  );
};

export default RightSidebar;
