import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import axios from 'axios';

interface OnlineStatusContextType {
  onlineUsers: string[];
  userDetails: { [key: string]: string };  // Maps userId to username
  addUser: (userId: string, username: string) => void;
  removeUser: (userId: string) => void;
  fetchAllUsers: () => void; // Add fetchAllUsers function
}

interface User {
  id: string;
  username: string;
}

const OnlineStatusContext = createContext<OnlineStatusContextType | undefined>(undefined);

interface OnlineStatusProviderProps {
  children: ReactNode;
}

export const OnlineStatusProvider: React.FC<OnlineStatusProviderProps> = ({ children }) => {
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [userDetails, setUserDetails] = useState<{ [key: string]: string }>({});

  const addUser = (userId: string, username: string) => {
    setOnlineUsers((prev) => [...prev, userId]);
    setUserDetails((prev) => ({ ...prev, [userId]: username }));
  };

  const removeUser = (userId: string) => {
    setOnlineUsers((prev) => prev.filter((id) => id !== userId));
    setUserDetails((prev) => {
      const newDetails = { ...prev };
      delete newDetails[userId];
      return newDetails;
    });
  };

  // Function to fetch all users and update state
  const fetchAllUsers = async () => {
    try {
      const response = await axios.get('/api/users');  // Adjust this URL to your API
      const users = response.data;
      users.forEach((user: User) => {
        setUserDetails((prev) => ({ ...prev, [user.id]: user.username }));
      });
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  useEffect(() => {
    // Fetch all users once when the component mounts
    fetchAllUsers();
  }, []);

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, userDetails, addUser, removeUser, fetchAllUsers }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = (): OnlineStatusContextType => {
  const context = useContext(OnlineStatusContext);
  if (!context) {
    throw new Error('useOnlineStatus must be used within an OnlineStatusProvider');
  }
  return context;
};
