// frontend/src/components/FeedItem/Story.tsx
import React from 'react';

interface StoryProps {
    story: {
        id: number;
        user: number;
        content: string;
        created_at: string;
        updated_at: string;
    };
}

const Story: React.FC<StoryProps> = ({ story }) => {
    return (
        <div className="story">
            <p>{story.content}</p>
        </div>
    );
};

export default Story;
