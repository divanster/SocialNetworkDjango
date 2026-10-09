import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Profile from './Profile';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      username: 'tester',
      profile: { profile_picture: null },
    },
  }),
}));

describe('LeftSidebar Profile', () => {
  it('friends shortcut routes to /friends', () => {
    render(
      <MemoryRouter>
        <Profile />
      </MemoryRouter>
    );

    const friendsLink = screen.getByRole('link', { name: /Friends/i });
    expect(friendsLink).toHaveAttribute('href', '/friends');
  });

  it('albums shortcut routes to /albums', () => {
    render(
      <MemoryRouter>
        <Profile />
      </MemoryRouter>
    );

    const albumsLink = screen.getByRole('link', { name: /Albums/i });
    expect(albumsLink).toHaveAttribute('href', '/albums');
  });
});
