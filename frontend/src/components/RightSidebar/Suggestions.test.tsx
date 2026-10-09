import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import Suggestions from './Suggestions';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ token: 'test-token' }),
}));

describe('Suggestions', () => {
  it('renders suggestion user identity link to profile route', async () => {
    (axios.get as jest.Mock).mockResolvedValueOnce({
      data: [
        {
          id: 'user-10',
          username: 'alice',
          full_name: 'Alice Stone',
          profile_picture: null,
          mutual_friends_count: 2,
        },
      ],
    });

    render(
      <MemoryRouter>
        <Suggestions />
      </MemoryRouter>
    );

    const link = await screen.findByRole('link', { name: 'Alice Stone' });
    expect(link).toHaveAttribute('href', '/profile/user-10');
  });
});
