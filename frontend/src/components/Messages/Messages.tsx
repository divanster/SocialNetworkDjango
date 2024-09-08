import React, { useEffect, useState } from 'react';
import { fetchMessages, sendMessage } from 'services/api'; // Assuming fetchMessages and sendMessage are defined
import { useAuth } from '../../contexts/AuthContext'; // Assuming useAuth is defined and provides isAuthenticated and token
import './Messages.css'; // Assuming CSS is handled separately

interface Message {
  id: number;
  sender: number;
  receiver: number;
  sender_name: string;
  receiver_name: string;
  content: string;
  timestamp: string;
  is_read: boolean;
}

interface User {
  id: number;
  username: string;
  email: string;
  profile_picture: string | null;
}

const Messages: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [receiverId, setReceiverId] = useState<number>(0);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);
  const [isLoadingUsers, setIsLoadingUsers] = useState<boolean>(false);
  const { isAuthenticated, token } = useAuth(); // Extract token from useAuth

  useEffect(() => {
    if (isAuthenticated && token) {
      // Fetch users when authenticated
      const fetchUsersAsync = async () => {
        setIsLoadingUsers(true);
        try {
          const response = await fetch('http://127.0.0.1:8000/api/users/users/', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          });
          if (!response.ok) {
            throw new Error('Failed to fetch users');
          }
          const data = await response.json();
          console.log('Fetched users:', data.results); // Debugging log
          setUsers(data.results || []); // Set users state
        } catch (error) {
          console.error('Error fetching users:', error);
          alert('Failed to fetch users. Please try again.');
        } finally {
          setIsLoadingUsers(false);
        }
      };

      // Fetch messages when authenticated
      const fetchMessagesAsync = async () => {
        setIsLoadingMessages(true);
        try {
          const fetchedMessages = await fetchMessages(); // Fetch messages
          console.log('API response (Messages):', fetchedMessages); // Debugging log
          setMessages(fetchedMessages); // Set messages state
        } catch (error) {
          console.error('Error fetching messages:', error);
          alert('Failed to fetch messages. Please try again.');
        } finally {
          setIsLoadingMessages(false);
        }
      };

      fetchUsersAsync();
      fetchMessagesAsync();
    }
  }, [isAuthenticated, token]); // Add token to dependency array

  const handleSendMessage = async () => {
    if (newMessage.trim() && receiverId) {
      try {
        await sendMessage(receiverId, newMessage); // Send message via API
        setNewMessage(''); // Clear input
        const updatedMessages = await fetchMessages(); // Re-fetch messages
        setMessages(updatedMessages); // Update state
      } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please try again.');
      }
    } else {
      alert('Please select a user and type a message before sending.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleSendMessage(); // Send message on form submit
  };

  console.log('Messages to render:', messages); // Debug log before rendering

  return (
    <div className="messages-container">
      <h2>Messages</h2>
      <div className="chat-section">
        {isLoadingMessages ? (
          <p>Loading messages...</p>
        ) : (
          <div className="messages-list">
            {messages.length === 0 ? (
              <p>No messages to display.</p>
            ) : (
              messages.map((message) => (
                <div key={message.id} className={`message ${message.is_read ? 'read' : 'unread'}`}>
                  <p>
                    <strong>{message.sender_name}:</strong> {message.content}{' '}
                    <em>({new Date(message.timestamp).toLocaleString()})</em>
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      <div className="send-message-section">
        {isLoadingUsers ? (
          <p>Loading users...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            {users.length === 0 ? (
              <p>No users available to message.</p>
            ) : (
              <select
                onChange={(e) => setReceiverId(Number(e.target.value))}
                value={receiverId}
                aria-label="Select user to message"
              >
                <option value={0}>Select a user</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username}
                  </option>
                ))}
              </select>
            )}
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type a message..."
              aria-label="Message input"
            />
            <button type="submit" disabled={!newMessage.trim() || !receiverId}>
              Send
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Messages;
