import React, { useEffect, useState } from 'react';
import { fetchUsers } from '../../services/api';  // Import the function to fetch all users
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';  // Import the context for online users
import { useWebSocketContext } from '../../contexts/WebSocketContext';  // Import WebSocketContext

const Contacts: React.FC = () => {
  const { onlineUsers, userDetails, addUser, removeUser } = useOnlineStatus();  // Get functions and data from the context
  const { subscribe, unsubscribe } = useWebSocketContext();  // Get subscribe and unsubscribe from WebSocketContext
  const [allUsers, setAllUsers] = useState<any[]>([]);  // State to hold all users

  useEffect(() => {
    const getAllUsers = async () => {
      const users = await fetchUsers();  // Call the function to fetch users
      setAllUsers(users);  // Set the fetched users
    };

    getAllUsers();  // Fetch all users on mount

    // Subscribe to the "users" WebSocket group
    subscribe('users');

    // Handle online status
    const handleOnlineStatus = (event: CustomEvent) => {
      const message = event.detail;
      if (message.type === 'user_online') {
        addUser(message.user_id, message.username);  // Add user when they go online
      } else if (message.type === 'user_offline') {
        removeUser(message.user_id);  // Remove user when they go offline
      }
    };

    window.addEventListener('ws-user_online', handleOnlineStatus);
    window.addEventListener('ws-user_offline', handleOnlineStatus);

    return () => {
      unsubscribe('users');  // Unsubscribe when the component unmounts
      window.removeEventListener('ws-user_online', handleOnlineStatus);
      window.removeEventListener('ws-user_offline', handleOnlineStatus);
    };
  }, [addUser, removeUser, subscribe, unsubscribe]);  // Add the functions to the dependency array

  return (
    <div>
      <h3>Contacts</h3>
      <h4>All Users</h4>
      <ul>
        {allUsers.length > 0 ? (
          allUsers.map((user) => (
            <li key={user.id}>
              {user.username} - {user.email}
              {/* Check if the user is online */}
              {onlineUsers.includes(user.id) ? (
                <span style={{ color: 'green' }}> (Online)</span>
              ) : (
                <span style={{ color: 'red' }}> (Offline)</span>
              )}
            </li>
          ))
        ) : (
          <li>No users found.</li>
        )}
      </ul>
    </div>
  );
};

export default Contacts;
