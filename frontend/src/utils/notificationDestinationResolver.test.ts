import { resolveNotificationDestination } from './notificationDestinationResolver';

describe('resolveNotificationDestination', () => {
  it('routes message notifications to messenger conversation', () => {
    const destination = resolveNotificationDestination({
      id: 'n-1',
      notification_type: 'message',
      sender_id: 'user-2',
      text: 'New message',
      read: false,
      created_at: '2026-01-01T00:00:00Z',
    });

    expect(destination).toEqual({
      canNavigate: true,
      path: '/messenger?userId=user-2',
    });
  });

  it('keeps unresolved notification types non-navigable', () => {
    const destination = resolveNotificationDestination({
      id: 'n-2',
      notification_type: 'tagged',
      text: 'You were tagged',
      read: false,
      created_at: '2026-01-01T00:00:00Z',
    });

    expect(destination).toEqual({
      canNavigate: false,
      path: null,
    });
  });
});
