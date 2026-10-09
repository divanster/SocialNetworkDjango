import React from 'react';
import Story from './Story';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import './StoryCarousel.css';

interface StoryProps {
  id: string;
  user: { id: string; full_name: string; profile_picture: string };
  content: string;
  created_at: string;
  updated_at: string;
}

interface Props {
  stories: StoryProps[];
}

const StoryCarousel: React.FC<Props> = ({ stories }) => {
  if (!stories.length) return null;

  return (
    <div className="stories-bar">
      {stories.slice(0, 6).map((st) => (
        <div key={st.id} className="story-wrapper">
          <UserIdentityLink userId={st.user.id} className="story-user" ariaLabel={`Open ${st.user.full_name} profile`}>
            <Avatar
              size={28}
              src={st.user.profile_picture}
              name={st.user.full_name}
              alt={`${st.user.full_name} avatar`}
            />
            <span>{st.user.full_name}</span>
          </UserIdentityLink>
          <Story
            story={{
              id: Number(st.id),
              user: Number(st.user.id),
              content: st.content,
              created_at: st.created_at,
              updated_at: st.updated_at,
            }}
          />
        </div>
      ))}
      {stories.length > 6 && <div className="story-scroll-hint">›</div>}
    </div>
  );
};

export default StoryCarousel;
