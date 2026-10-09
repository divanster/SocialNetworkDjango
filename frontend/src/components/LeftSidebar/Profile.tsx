import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BsFillHouseDoorFill, BsPeopleFill, BsImages, BsCollectionPlay, BsMessenger, BsBellFill } from 'react-icons/bs';
import { useAuth } from '../../contexts/AuthContext';
import Avatar from '../Common/Avatar';
import { profileBasePath } from '../../utils/profileRoutes';
import './Profile.css';

const shortcuts = [
  { key: 'profile', label: 'My Profile', icon: <BsPeopleFill />, to: profileBasePath },
  { key: 'feed', label: 'Feed', icon: <BsFillHouseDoorFill />, to: '/' },
  { key: 'friends', label: 'Friends', icon: <BsPeopleFill />, to: '/' },
  { key: 'albums', label: 'Albums', icon: <BsImages />, to: '/#albums' },
  { key: 'stories', label: 'Stories', icon: <BsCollectionPlay />, to: '/#stories' },
  { key: 'messenger', label: 'Messenger', icon: <BsMessenger />, to: '/messenger' },
  { key: 'notifications', label: 'Notifications', icon: <BsBellFill />, to: '/' },
];

const Profile: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const displayName = user?.username || 'User';

  return (
    <div className="left-profile-card">
      <div className="left-profile-header">
        <Avatar
          size={48}
          src={user?.profile?.profile_picture}
          name={displayName}
          alt={`${displayName} avatar`}
        />
        <div>
          <Link className="left-profile-name-link" to={profileBasePath}>
            <div className="left-profile-name">{displayName}</div>
            <div className="left-profile-subtitle">View your profile</div>
          </Link>
        </div>
      </div>

      <nav aria-label="Shortcuts">
        <ul className="left-shortcuts">
          {shortcuts.map((item) => {
            const isActive =
              (item.to === '/' && location.pathname === '/') ||
              (item.to === '/messenger' && location.pathname.startsWith('/messenger')) ||
              (item.to === profileBasePath && location.pathname.startsWith(profileBasePath));
            return (
              <li key={item.key}>
                <Link className={`shortcut-link ${isActive ? 'active' : ''}`} to={item.to}>
                  <span className="shortcut-icon" aria-hidden="true">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
};

export default Profile;
