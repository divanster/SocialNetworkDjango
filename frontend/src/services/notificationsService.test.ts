import axios from 'axios';
import {
  listNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
} from './notificationsService';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('notificationsService', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('uses canonical mark_as_read endpoint', async () => {
    mockedAxios.post.mockResolvedValue({ data: {} } as any);
    await markNotificationAsRead('notif-1');
    expect(mockedAxios.post).toHaveBeenCalledWith('/notifications/notif-1/mark_as_read/');
  });

  it('uses canonical mark all endpoint', async () => {
    mockedAxios.post.mockResolvedValue({ data: {} } as any);
    await markAllNotificationsAsRead();
    expect(mockedAxios.post).toHaveBeenCalledWith('/notifications/mark_all_as_read/');
  });

  it('supports paginated list response', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { results: [{ id: 'n-1', text: 'hi', read: false, notification_type: 'message', created_at: '2026-01-01T00:00:00Z' }] },
    } as any);

    const result = await listNotifications();
    expect(result).toHaveLength(1);
    expect(mockedAxios.get).toHaveBeenCalledWith('/notifications/');
  });
});
