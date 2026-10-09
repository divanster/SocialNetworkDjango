import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NotificationsPage from './NotificationsPage';
import * as notificationsService from '../services/notificationsService';

const mockNavigate = jest.fn();

jest.mock('../hooks/useWebSocket', () => ({
  __esModule: true,
  default: () => ({ sendMessage: jest.fn() }),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('NotificationsPage', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
    mockNavigate.mockReset();
  });

  it('shows empty state when no notifications', async () => {
    jest.spyOn(notificationsService, 'listNotifications').mockResolvedValue([]);
    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('No notifications yet.')).toBeInTheDocument();
  });

  it('shows retryable error state', async () => {
    jest.spyOn(notificationsService, 'listNotifications').mockRejectedValue(new Error('fail'));
    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('Failed to load notifications.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });

  it('navigates for resolvable notification and skips unresolved', async () => {
    jest.spyOn(notificationsService, 'listNotifications').mockResolvedValue([
      {
        id: 'n-1',
        notification_type: 'message',
        text: 'Message received',
        read: false,
        created_at: '2026-01-01T00:00:00Z',
        sender_id: 'friend-1',
        sender_username: 'friend1',
      },
      {
        id: 'n-2',
        notification_type: 'tagged',
        text: 'Tagged in content',
        read: false,
        created_at: '2026-01-01T00:01:00Z',
      },
    ]);
    jest.spyOn(notificationsService, 'markNotificationAsRead').mockResolvedValue();

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByText('Message received'));
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/messenger?userId=friend-1'));

    fireEvent.click(screen.getByText('Tagged in content'));
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledTimes(1));
  });
});
