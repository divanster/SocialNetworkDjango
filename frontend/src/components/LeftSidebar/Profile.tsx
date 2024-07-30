// frontend/src/components/LeftSidebar/Profile.tsx
import React from 'react';

const Profile: React.FC = () => {
    return (
        <div className="profile">
            <img src="/path/to/profile-pic.jpg" alt="Profile" className="img-fluid rounded-circle" />
            <h3>Your Name</h3>
            <ul>
                <li>Friends</li>
                <li>Pages</li>
                {/* Add more items as needed */}
            </ul>
        </div>
    );
};

export default Profile;
