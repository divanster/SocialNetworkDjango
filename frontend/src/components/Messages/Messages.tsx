import React, { useEffect, useState } from 'react';
import { fetchMessages, sendMessage, fetchUsers } from 'services/api';
import { useAuth } from '../../contexts/AuthContext';
import './Messages.css';

interface Message {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  timestamp: string;
  is_read: boolean;
}

interface User {
  id: number;
  username: string;
}

const Messages: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [receiverId, setReceiverId] = useState<number>(0);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);
  const [isLoadingUsers, setIsLoadingUsers] = useState<boolean>(false);
  const { isAuthenticated } = useAuth(); // Assuming isAuthenticated determines if the user is logged in

  useEffect(() => {
    if (isAuthenticated) {
      const fetchMessagesAsync = async () => {
        setIsLoadingMessages(true);
        try {
          const fetchedMessages = await fetchMessages();
          setMessages(fetchedMessages.results || []);
          console.log('Fetched messages:', fetchedMessages);
        } catch (error) {
          console.error('Error fetching messages:', error);
        } finally {
          setIsLoadingMessages(false);
        }
      };

      const fetchUsersAsync = async () => {
        setIsLoadingUsers(true);
        try {
          const fetchedUsers = await fetchUsers();
          setUsers(fetchedUsers || []);
          console.log('Fetched users:', fetchedUsers);
        } catch (error) {
          console.error('Error fetching users:', error);
          setUsers([]);
        } finally {
          setIsLoadingUsers(false);
        }
      };

      fetchMessagesAsync();
      fetchUsersAsync();
    }
  }, [isAuthenticated]);

  const handleSendMessage = async () => {
    if (newMessage.trim() && receiverId) {
      try {
        await sendMessage(receiverId, newMessage);
        setNewMessage('');
        const updatedMessages = await fetchMessages(); // Refresh message list after sending
        setMessages(updatedMessages.results || []);
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleSendMessage();
  };

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
                <div key={message.id} className="message">
                  <p>
                    <strong>{message.sender}:</strong> {message.content}{' '}
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
