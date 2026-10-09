import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from './Navbar';
import { fetchMessagesCount, fetchNotificationsCount } from '../../services/api';

const mockLogout = jest.fn();
const mockNavigate = jest.fn();

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    logout: mockLogout,
    user: {
      username: 'tester',
      profile: { profile_picture: null },
    },
  }),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

jest.mock('../../services/api', () => ({
  API_URL: '/api/v1',
  fetchMessagesCount: jest.fn().mockResolvedValue(0),
  fetchNotificationsCount: jest.fn().mockResolvedValue(0),
}));

jest.mock('../Search/SearchBar', () => () => <div>Search</div>);
jest.mock('./NotificationsDropdown', () => () => <div>Notifications</div>);
jest.mock('./MessagesDropdown', () => () => <div>Messages</div>);

describe('Navbar', () => {
  const mockedFetchMessagesCount = fetchMessagesCount as jest.MockedFunction<typeof fetchMessagesCount>;
  const mockedFetchNotificationsCount = fetchNotificationsCount as jest.MockedFunction<typeof fetchNotificationsCount>;

  beforeEach(() => {
    mockLogout.mockReset();
    mockNavigate.mockReset();
    mockedFetchMessagesCount.mockResolvedValue(0);
    mockedFetchNotificationsCount.mockResolvedValue(0);
  });

  it('friends control routes to /friends', async () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    await waitFor(() => expect(mockedFetchMessagesCount).toHaveBeenCalled());
    const friendsLink = await screen.findByRole('link', { name: 'Friends' });
    expect(friendsLink).toHaveAttribute('href', '/friends');
  });

  it('shows mobile nav links to primary routes', async () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    await waitFor(() => expect(mockedFetchNotificationsCount).toHaveBeenCalled());
    fireEvent.click(screen.getByLabelText('Toggle navigation'));
    const mobileNav = screen.getByLabelText('Mobile primary navigation');
    expect(within(mobileNav).getByRole('link', { name: 'My Profile' })).toHaveAttribute('href', '/profile');
    expect(within(mobileNav).getByRole('link', { name: 'Albums' })).toHaveAttribute('href', '/albums');
  });

  it('mobile logout action logs out and redirects to /login', async () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    await waitFor(() => expect(mockedFetchMessagesCount).toHaveBeenCalled());
    fireEvent.click(screen.getByLabelText('Toggle navigation'));
    const mobileNav = screen.getByLabelText('Mobile primary navigation');
    fireEvent.click(within(mobileNav).getByRole('button', { name: 'Logout' }));
    expect(mockLogout).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
