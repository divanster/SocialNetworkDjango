// frontend/src/components/FeedItem/Reaction.tsx
import React from 'react';

interface ReactionProps {
    reaction: {
        id: number;
        user: number;
        post: number;
        emoji: string;
        created_at: string;
    };
}

const Reaction: React.FC<ReactionProps> = ({ reaction }) => {
    return (
        <div className="reaction">
            <p><strong>User:</strong> {reaction.user}</p>
            <p><strong>Emoji:</strong> {reaction.emoji}</p>
        </div>
    );
};

export default Reaction;
