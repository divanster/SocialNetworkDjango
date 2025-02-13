// frontend/src/components/RightSidebar/Contacts.tsx
import React, { useEffect } from 'react';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext'; // Import the context

const Contacts: React.FC = () => {
  const { onlineUsers, addUser, removeUser } = useOnlineStatus();

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/presence/');  // WebSocket URL for presence

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'user_online') {
        addUser(data.userId);  // Add user to online list
      } else if (data.type === 'user_offline') {
        removeUser(data.userId);  // Remove user from online list
      }
    };

    return () => {
      socket.close();  // Clean up WebSocket connection when the component unmounts
    };
  }, [addUser, removeUser]);

  return (
    <div>
      <h3>Contacts</h3>
      <ul>
        {onlineUsers.length > 0 ? (
          onlineUsers.map((userId) => (
            <li key={userId}>
              User ID: {userId} - <strong>Online</strong>
            </li>
          ))
        ) : (
          <li>No contacts online.</li>
        )}
      </ul>
    </div>
  );
};

export default Contacts;

