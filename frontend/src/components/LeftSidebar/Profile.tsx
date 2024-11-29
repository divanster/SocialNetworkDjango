import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_picture: string | null;
  bio: string;
  phone: string | null;
  town: string | null;
  country: string | null;
  relationship_status: string;
}

const Profile: React.FC = () => {
  const { token } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (token) {
        try {
          const response = await fetch('http://127.0.0.1:8000/api/v1/users/me/', {
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
        } catch (error: any) {
          setError(error.message);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchProfile();
  }, [token]);

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (error) {
    return <p>Error fetching profile: {error}</p>;
  }

  return (
    <div>
      {profile ? (
        <div>
          <h2>{profile.username}</h2>
          <p>{profile.first_name} {profile.last_name}</p>
          <p>{profile.email}</p>
          {profile.profile_picture ? (
            <img src={profile.profile_picture} alt="Profile" />
          ) : (
            <p>No profile picture</p>
          )}
          <p>Bio: {profile.bio}</p>
          <p>Phone: {profile.phone}</p>
          <p>Location: {profile.town}, {profile.country}</p>
          <p>Relationship Status: {profile.relationship_status}</p>
        </div>
      ) : (
        <p>No profile data available.</p>
      )}
    </div>
  );
};

export default Profile;
