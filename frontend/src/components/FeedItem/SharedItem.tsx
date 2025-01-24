// frontend/src/components/FeedItem/SharedItem.tsx

import React from 'react';
import { SharedItem as SharedItemType } from '../../types/sharedItem';
import './SharedItem.css'; // Ensure SharedItem.css exists or remove this line
import { useAuth } from '../../contexts/AuthContext';

interface SharedItemProps {
    sharedItems: SharedItemType[];
    onDeleteSharedItem: (id: string) => void;
}

const SharedItem: React.FC<SharedItemProps> = ({ sharedItems, onDeleteSharedItem }) => {
    const { user } = useAuth(); // Access the user object

    if (sharedItems.length === 0) {
        return <div className="shared-items">No shared content available.</div>;
    }

    return (
        <div className="shared-items">
            {sharedItems.map((item) => {
                const sharedByFullName = item.shared_by?.full_name || 'Unknown User';
                const originalAuthorFullName = item.original_author?.full_name || 'Unknown Author';

                return (
                    <div key={item.id} className="shared-item-card">
                        <div className="shared-item-header">
                            <img
                                src={item.shared_by?.profile_picture || '/default-profile.png'}
                                alt={`${item.shared_by?.username || 'unknown_user'}'s profile`}
                                style={{
                                    width: '50px',
                                    height: '50px',
                                    borderRadius: '50%',
                                    objectFit: 'cover',
                                    marginRight: '12px',
                                }}
                            />
                            <div>
                                <strong>{sharedByFullName}</strong> shared a post
                                <span>{new Date(item.created_at).toLocaleString()}</span>
                            </div>
                            {user && String(item.shared_by?.id) === String(user.id) && (
                                <button
                                    onClick={() => onDeleteSharedItem(item.id)}
                                    className="delete-button"
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: '#e74c3c',
                                        fontSize: '1.2em',
                                        cursor: 'pointer',
                                    }}
                                >
                                    &times;
                                </button>
                            )}
                        </div>
                        <div className="shared-item-content">
                            <p>{item.content}</p>
                            <div className="original-content">
                                <strong>{originalAuthorFullName}'s post:</strong>
                                <p>{item.original_content}</p>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default SharedItem;
