import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NotificationsDropdown from './NotificationsDropdown';
import * as notificationsService from '../../services/notificationsService';

let socketHandler: ((payload: any) => void) | null = null;

jest.mock('../../hooks/useWebSocket', () => ({
  __esModule: true,
  default: (_group: string, handlers: any) => {
    socketHandler = handlers.onMessage;
    return { sendMessage: jest.fn() };
  },
}));

describe('NotificationsDropdown', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
    socketHandler = null;
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
    ]);
    jest.spyOn(notificationsService, 'markNotificationAsRead').mockResolvedValue();
    jest.spyOn(notificationsService, 'markAllNotificationsAsRead').mockResolvedValue();
  });

  it('renders notifications from API', async () => {
    const setUnreadCount = jest.fn();
    render(
      <MemoryRouter>
        <NotificationsDropdown unreadCount={1} setUnreadCount={setUnreadCount} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Notifications/i));
    expect(await screen.findByText('Message received')).toBeInTheDocument();
    expect(setUnreadCount).toHaveBeenCalledWith(1);
  });

  it('marks one notification as read', async () => {
    render(
      <MemoryRouter>
        <NotificationsDropdown unreadCount={1} setUnreadCount={jest.fn()} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Notifications/i));
    fireEvent.click(await screen.findByText('Message received'));
    await waitFor(() => expect(notificationsService.markNotificationAsRead).toHaveBeenCalledWith('n-1'));
  });

  it('marks all notifications as read', async () => {
    render(
      <MemoryRouter>
        <NotificationsDropdown unreadCount={1} setUnreadCount={jest.fn()} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Notifications/i));
    fireEvent.click(await screen.findByRole('button', { name: 'Mark all as read' }));
    await waitFor(() => expect(notificationsService.markAllNotificationsAsRead).toHaveBeenCalled());
  });

  it('handles realtime insert de-duplication', async () => {
    render(
      <MemoryRouter>
        <NotificationsDropdown unreadCount={1} setUnreadCount={jest.fn()} />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByText(/Notifications/i));
    await screen.findByText('Message received');

    const incoming = {
      type: 'notification',
      data: {
        id: 'n-2',
        notification_type: 'message',
        text: 'Realtime',
        read: false,
        created_at: '2026-01-01T00:01:00Z',
        sender_id: 'friend-2',
        sender_username: 'friend2',
      },
    };
    await act(async () => {
      socketHandler?.(incoming);
      socketHandler?.(incoming);
    });

    await waitFor(() => expect(screen.getAllByText('Realtime')).toHaveLength(1));
  });
});
