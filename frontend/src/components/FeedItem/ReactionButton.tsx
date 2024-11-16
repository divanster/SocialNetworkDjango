// frontend/src/components/FeedItem/ReactionButton.tsx

import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface ReactionButtonProps {
  postId: number;
}

const ReactionButton: React.FC<ReactionButtonProps> = ({ postId }) => {
  const { token } = useAuth();
  const [reactionsCount, setReactionsCount] = useState(0);

  const handleReaction = async () => {
    if (!token) {
      console.error('No authentication token available.');
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/posts/${postId}/reactions/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setReactionsCount(response.data.reactionsCount);
    } catch (error) {
      console.error('Error reacting to post', error);
    }
  };

  return (
    <Button onClick={handleReaction}>
      Like {reactionsCount > 0 && <span>({reactionsCount})</span>}
    </Button>
  );
};

export default ReactionButton;
