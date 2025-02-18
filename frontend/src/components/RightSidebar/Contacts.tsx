import React, { useEffect, useState } from 'react';
import { fetchUsers } from '../../services/api';  // Import the function to fetch all users
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';  // Import the context for online users

const Contacts: React.FC = () => {
  const { onlineUsers } = useOnlineStatus();  // Get online users from context
  const [allUsers, setAllUsers] = useState<any[]>([]);  // State to hold all users

  useEffect(() => {
    // Fetch all users from the API when the component mounts
    const getAllUsers = async () => {
      const users = await fetchUsers();
      setAllUsers(users);
    };

    getAllUsers();  // Call the function to fetch users
  }, []);  // Empty dependency array to run this effect only once when the component mounts

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
