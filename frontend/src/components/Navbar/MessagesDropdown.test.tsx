import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MessagesDropdown from './MessagesDropdown';
import * as messagesService from '../../services/messagesService';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

jest.mock('../../hooks/useWebSocket', () => ({
  __esModule: true,
  default: () => ({ sendMessage: jest.fn() }),
}));

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'me-1' },
  }),
}));

describe('MessagesDropdown', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
    mockNavigate.mockReset();
    jest.spyOn(messagesService, 'fetchInboxMessages').mockResolvedValue([
      {
        id: 'm-1',
        sender: { id: 'friend-1', username: 'friend1', full_name: 'Friend One', profile_picture: null },
        receiver: { id: 'me-1', username: 'me', full_name: 'Me', profile_picture: null },
        content: 'Hello there',
        read: false,
        created_at: '2026-01-01T00:00:00Z',
      },
    ] as any);
    jest.spyOn(messagesService, 'markMessageAsRead').mockResolvedValue();
  });

  it('routes dropdown item to messenger query route', async () => {
    const setUnreadCount = jest.fn();
    render(
      <MemoryRouter>
        <MessagesDropdown unreadCount={1} setUnreadCount={setUnreadCount} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Messages/i));
    fireEvent.click(await screen.findByRole('button', { name: /Open conversation with Friend One/i }));
    await waitFor(() => expect(messagesService.markMessageAsRead).toHaveBeenCalledWith('m-1'));
    expect(mockNavigate).toHaveBeenCalledWith('/messenger?userId=friend-1');
  });

  it('contains view all messages link to /messenger', async () => {
    render(
      <MemoryRouter>
        <MessagesDropdown unreadCount={1} setUnreadCount={jest.fn()} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Messages/i));
    const viewAll = await screen.findByText('View all messages');
    expect(viewAll).toHaveAttribute('href', '/messenger');
  });

  it('marks unread message read from dropdown selection', async () => {
    const setUnreadCount = jest.fn();
    render(
      <MemoryRouter>
        <MessagesDropdown unreadCount={1} setUnreadCount={setUnreadCount} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Messages/i));
    fireEvent.click(await screen.findByRole('button', { name: /Open conversation with Friend One/i }));
    await waitFor(() => expect(messagesService.markMessageAsRead).toHaveBeenCalledWith('m-1'));
  });
});
