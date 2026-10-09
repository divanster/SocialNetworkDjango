import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from './Navbar';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    logout: jest.fn(),
    user: {
      username: 'tester',
      profile: { profile_picture: null },
    },
  }),
}));

jest.mock('../../services/api', () => ({
  API_URL: 'http://localhost:8001/api/v1',
  fetchMessagesCount: jest.fn().mockResolvedValue(0),
  fetchNotificationsCount: jest.fn().mockResolvedValue(0),
}));

jest.mock('../Search/SearchBar', () => () => <div>Search</div>);
jest.mock('./NotificationsDropdown', () => () => <div>Notifications</div>);
jest.mock('./MessagesDropdown', () => () => <div>Messages</div>);

describe('Navbar', () => {
  it('friends control routes to /friends', async () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    const friendsLink = await screen.findByRole('link', { name: 'Friends' });
    expect(friendsLink).toHaveAttribute('href', '/friends');
  });
});
