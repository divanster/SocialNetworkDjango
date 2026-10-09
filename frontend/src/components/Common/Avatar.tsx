import React, { useMemo, useState } from 'react';
import './Avatar.css';

interface AvatarProps {
  src?: string | null;
  name?: string;
  size?: number;
  alt?: string;
  className?: string;
  showOnline?: boolean;
}

const Avatar: React.FC<AvatarProps> = ({
  src,
  name = 'User',
  size = 40,
  alt,
  className = '',
  showOnline = false,
}) => {
  const [hasError, setHasError] = useState(false);

  const initials = useMemo(() => {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return 'U';
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }, [name]);

  const resolvedAlt = alt || `${name} avatar`;
  const showImage = Boolean(src) && !hasError;

  return (
    <span
      className={`avatar ${className}`.trim()}
      style={{ width: size, height: size }}
      aria-label={resolvedAlt}
    >
      {showImage ? (
        <img
          className="avatar__img"
          src={src as string}
          alt={resolvedAlt}
          onError={() => setHasError(true)}
        />
      ) : (
        <span className="avatar__fallback" aria-hidden="true">
          {initials}
        </span>
      )}
      {showOnline && <span className="avatar__status" aria-hidden="true" />}
    </span>
  );
};

export default Avatar;

