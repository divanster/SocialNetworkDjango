import axios from 'axios';
import { blockUser, followUser, sendFriendRequest, unfollowUser } from './socialGraphService';

describe('socialGraphService contracts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (axios.post as jest.Mock).mockResolvedValue({ data: { id: 'x' } });
    (axios.delete as jest.Mock).mockResolvedValue({});
  });

  it('sendFriendRequest uses canonical receiver_id payload', async () => {
    await sendFriendRequest('target-user');
    expect(axios.post).toHaveBeenCalledWith('/friends/friend-requests/', { receiver_id: 'target-user' });
  });

  it('followUser uses canonical followed payload', async () => {
    await followUser('target-user');
    expect(axios.post).toHaveBeenCalledWith('/follows/', { followed: 'target-user' });
  });

  it('unfollowUser uses canonical delete endpoint', async () => {
    await unfollowUser('follow-id-1');
    expect(axios.delete).toHaveBeenCalledWith('/follows/follow-id-1/');
  });

  it('blockUser uses canonical blocked_id payload', async () => {
    await blockUser('target-user');
    expect(axios.post).toHaveBeenCalledWith('/friends/blocks/', { blocked_id: 'target-user' });
  });
});
