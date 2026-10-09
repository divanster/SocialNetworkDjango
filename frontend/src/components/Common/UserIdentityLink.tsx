import React from 'react';
import { Link } from 'react-router-dom';
import { buildProfilePath, hasValidUserId } from '../../utils/profileRoutes';
import './UserIdentityLink.css';

interface UserIdentityLinkProps {
  userId?: string | null;
  className?: string;
  children: React.ReactNode;
  ariaLabel?: string;
  onClick?: React.MouseEventHandler<HTMLElement>;
}

const UserIdentityLink: React.FC<UserIdentityLinkProps> = ({
  userId,
  className = '',
  children,
  ariaLabel,
  onClick,
}) => {
  if (!hasValidUserId(userId)) {
    return (
      <span className={className} onClick={onClick}>
        {children}
      </span>
    );
  }

  return (
    <Link
      to={buildProfilePath(userId)}
      className={`user-identity-link ${className}`.trim()}
      aria-label={ariaLabel}
      onClick={onClick}
    >
      {children}
    </Link>
  );
};

export default UserIdentityLink;
