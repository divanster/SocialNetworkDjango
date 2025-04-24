import React from 'react';
import Story from './Story';
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
