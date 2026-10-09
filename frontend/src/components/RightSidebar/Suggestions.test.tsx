import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Suggestions from './Suggestions';
import { fetchUserSuggestions, sendFriendRequest } from '../../services/socialGraphService';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ token: 'test-token' }),
}));

jest.mock('../../services/socialGraphService', () => ({
  ...jest.requireActual('../../services/socialGraphService'),
  fetchUserSuggestions: jest.fn(),
  sendFriendRequest: jest.fn().mockResolvedValue({ id: 'request-1' }),
}));

describe('Suggestions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders suggestion user identity link to profile route', async () => {
    (fetchUserSuggestions as jest.Mock).mockResolvedValueOnce([
      {
        id: 'user-10',
        username: 'alice',
        full_name: 'Alice Stone',
        profile_picture: null,
        mutual_friends_count: 2,
      },
    ]);

    render(
      <MemoryRouter>
        <Suggestions />
      </MemoryRouter>
    );

    const link = await screen.findByRole('link', { name: 'Alice Stone' });
    expect(link).toHaveAttribute('href', '/profile/user-10');
  });

  it('sends friend request when Add Friend is clicked', async () => {
    (fetchUserSuggestions as jest.Mock).mockResolvedValueOnce([
      {
        id: 'user-11',
        username: 'bob',
        full_name: 'Bob Stone',
        profile_picture: null,
        mutual_friends_count: 0,
      },
    ]);

    render(
      <MemoryRouter>
        <Suggestions />
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole('button', { name: 'Add Friend' }));
    await waitFor(() => {
      expect(sendFriendRequest).toHaveBeenCalledWith('user-11');
    });
  });
});
