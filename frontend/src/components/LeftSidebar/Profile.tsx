// frontend/src/components/LeftSidebar/Profile.tsx

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  profile_picture: string | null;
}

const Profile: React.FC = () => {
  const { token } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (token) {
        try {
          const response = await fetch('http://127.0.0.1:8000/api/users/profile/', {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          });
          if (!response.ok) {
            throw new Error('Failed to fetch profile');
          }
          const data = await response.json();
          setProfile(data);
        } catch (error) {
          console.error('Error fetching profile:', error);
        }
      }
    };

    fetchProfile();
  }, [token]);

  return (
    <div>
      {profile ? (
        <div>
          <h2>{profile.username}</h2>
          <p>{profile.email}</p>
          {/* Display profile picture and other details */}
        </div>
      ) : (
        <p>Loading profile...</p>
      )}
    </div>
  );
};

export default Profile;
