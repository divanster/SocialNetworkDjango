import axios from 'axios';
import { markMessageAsRead, sendMessageToUser } from './messagesService';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('messagesService', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('uses canonical mark_as_read endpoint', async () => {
    mockedAxios.post.mockResolvedValue({ data: {} } as any);
    await markMessageAsRead('message-1');
    expect(mockedAxios.post).toHaveBeenCalledWith('/messenger/message-1/mark_as_read/');
  });

  it('sends canonical message payload', async () => {
    mockedAxios.post.mockResolvedValue({
      data: {
        id: 'message-2',
        sender: 'me',
        receiver: 'user-2',
        sender_name: 'me',
        receiver_name: 'user2',
        sender_full_name: 'Me',
        receiver_full_name: 'User Two',
        sender_profile_picture: null,
        receiver_profile_picture: null,
        content: 'hello',
        read: false,
        created_at: '2026-01-01T00:00:00Z',
      },
    } as any);

    await sendMessageToUser('user-2', 'hello');
    expect(mockedAxios.post).toHaveBeenCalledWith('/messenger/', {
      receiver: 'user-2',
      content: 'hello',
    });
  });
});
