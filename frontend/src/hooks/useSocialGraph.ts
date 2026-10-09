import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  acceptFriendRequest,
  BlockItem,
  blockUser,
  cancelFriendRequest,
  fetchBlocks,
  fetchFollows,
  fetchFriendRequests,
  fetchFriendships,
  FollowItem,
  followUser,
  FriendRequestItem,
  FriendshipItem,
  rejectFriendRequest,
  removeFriendship,
  sendFriendRequest,
  unblockUser,
  unfollowUser,
} from '../services/socialGraphService';
import { emitSocialGraphUpdated, subscribeSocialGraphUpdated } from '../utils/socialGraphEvents';

export type FriendRelationState = 'none' | 'outgoing_pending' | 'incoming_pending' | 'friends';

export interface RelationshipState {
  isOwnProfile: boolean;
  friendState: FriendRelationState;
  following: boolean;
  blockedByCurrentUser: boolean;
  blockedByOtherUserKnown: boolean;
  blockedByOtherUser: boolean;
  canMessage: boolean;
  outgoingRequest?: FriendRequestItem;
  incomingRequest?: FriendRequestItem;
  friendship?: FriendshipItem;
  follow?: FollowItem;
  block?: BlockItem;
}

type ActionKey =
  | 'add_friend'
  | 'cancel_request'
  | 'accept_request'
  | 'reject_request'
  | 'remove_friend'
  | 'follow'
  | 'unfollow'
  | 'block'
  | 'unblock';

const initialActionLoading: Record<ActionKey, boolean> = {
  add_friend: false,
  cancel_request: false,
  accept_request: false,
  reject_request: false,
  remove_friend: false,
  follow: false,
  unfollow: false,
  block: false,
  unblock: false,
};

export const useSocialGraph = () => {
  const { user } = useAuth();
  const [friendRequests, setFriendRequests] = useState<FriendRequestItem[]>([]);
  const [friendships, setFriendships] = useState<FriendshipItem[]>([]);
  const [follows, setFollows] = useState<FollowItem[]>([]);
  const [blocks, setBlocks] = useState<BlockItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<Record<ActionKey, boolean>>(initialActionLoading);

  const currentUserId = user?.id || '';

  const refresh = useCallback(async () => {
    if (!currentUserId) {
      setFriendRequests([]);
      setFriendships([]);
      setFollows([]);
      setBlocks([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [requestsData, friendshipsData, followsData, blocksData] = await Promise.all([
        fetchFriendRequests(),
        fetchFriendships(),
        fetchFollows(currentUserId),
        fetchBlocks(),
      ]);
      setFriendRequests(requestsData);
      setFriendships(friendshipsData);
      setFollows(followsData);
      setBlocks(blocksData);
    } catch (err) {
      setError('Could not load social relationship data.');
    } finally {
      setLoading(false);
    }
  }, [currentUserId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => subscribeSocialGraphUpdated(refresh), [refresh]);

  const executeAction = useCallback(async (key: ActionKey, operation: () => Promise<void>) => {
    setActionLoading((prev) => ({ ...prev, [key]: true }));
    setActionError(null);
    try {
      await operation();
      await refresh();
      emitSocialGraphUpdated();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      const nonFieldErrors = err?.response?.data?.non_field_errors;
      if (Array.isArray(nonFieldErrors) && nonFieldErrors.length > 0) {
        setActionError(String(nonFieldErrors[0]));
      } else if (typeof detail === 'string' && detail.trim()) {
        setActionError(detail);
      } else {
        setActionError('Action failed. Please retry.');
      }
      throw err;
    } finally {
      setActionLoading((prev) => ({ ...prev, [key]: false }));
    }
  }, [refresh]);

  const deriveRelationship = useCallback((targetUserId: string): RelationshipState => {
    const isOwnProfile = targetUserId === currentUserId;
    const block = blocks.find((item) => item.blocked?.id === targetUserId);
    const blockedByCurrentUser = Boolean(block);

    const friendship = friendships.find(
      (item) => item.user1.id === targetUserId || item.user2.id === targetUserId
    );

    const incomingRequest = friendRequests.find(
      (item) =>
        item.status === 'pending' &&
        item.sender?.id === targetUserId &&
        item.receiver?.id === currentUserId
    );
    const outgoingRequest = friendRequests.find(
      (item) =>
        item.status === 'pending' &&
        item.sender?.id === currentUserId &&
        item.receiver?.id === targetUserId
    );

    const follow = follows.find((item) => item.followed === targetUserId);
    const following = Boolean(follow);

    let friendState: FriendRelationState = 'none';
    if (friendship) {
      friendState = 'friends';
    } else if (incomingRequest) {
      friendState = 'incoming_pending';
    } else if (outgoingRequest) {
      friendState = 'outgoing_pending';
    }

    return {
      isOwnProfile,
      friendState,
      following,
      blockedByCurrentUser,
      blockedByOtherUserKnown: false,
      blockedByOtherUser: false,
      canMessage: !isOwnProfile && !blockedByCurrentUser,
      outgoingRequest,
      incomingRequest,
      friendship,
      follow,
      block,
    };
  }, [blocks, currentUserId, follows, friendships, friendRequests]);

  const clearActionError = () => setActionError(null);

  const api = useMemo(() => ({
    addFriend: async (targetUserId: string) =>
      executeAction('add_friend', async () => {
        await sendFriendRequest(targetUserId);
      }),
    cancelOutgoingRequest: async (requestId: string) =>
      executeAction('cancel_request', async () => {
        await cancelFriendRequest(requestId);
      }),
    acceptIncomingRequest: async (requestId: string) =>
      executeAction('accept_request', async () => {
        await acceptFriendRequest(requestId);
      }),
    rejectIncomingRequest: async (requestId: string) =>
      executeAction('reject_request', async () => {
        await rejectFriendRequest(requestId);
      }),
    removeFriend: async (friendshipId: string) =>
      executeAction('remove_friend', async () => {
        await removeFriendship(friendshipId);
      }),
    follow: async (targetUserId: string) =>
      executeAction('follow', async () => {
        await followUser(targetUserId);
      }),
    unfollow: async (followId: string) =>
      executeAction('unfollow', async () => {
        await unfollowUser(followId);
      }),
    block: async (targetUserId: string) =>
      executeAction('block', async () => {
        await blockUser(targetUserId);
      }),
    unblock: async (blockId: string) =>
      executeAction('unblock', async () => {
        await unblockUser(blockId);
      }),
  }), [executeAction]);

  return {
    currentUserId,
    friendRequests,
    friendships,
    follows,
    blocks,
    loading,
    error,
    actionError,
    actionLoading,
    refresh,
    deriveRelationship,
    clearActionError,
    ...api,
  };
};
