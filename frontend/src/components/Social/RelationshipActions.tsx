import React from 'react';
import { Alert, Button } from 'react-bootstrap';
import { RelationshipState } from '../../hooks/useSocialGraph';

interface RelationshipActionsProps {
  relationship?: RelationshipState | null;
  targetUserId: string;
  actionLoading: Record<string, boolean>;
  actionError?: string | null;
  onAddFriend: (userId: string) => Promise<void>;
  onCancelRequest: (requestId: string) => Promise<void>;
  onAcceptRequest: (requestId: string) => Promise<void>;
  onRejectRequest: (requestId: string) => Promise<void>;
  onRemoveFriend: (friendshipId: string) => Promise<void>;
  onFollow: (userId: string) => Promise<void>;
  onUnfollow: (followId: string) => Promise<void>;
  onBlock: (userId: string) => Promise<void>;
  onUnblock: (blockId: string) => Promise<void>;
  onMessage?: () => void;
  hideMessage?: boolean;
}

const RelationshipActions: React.FC<RelationshipActionsProps> = ({
  relationship,
  targetUserId,
  actionLoading,
  actionError,
  onAddFriend,
  onCancelRequest,
  onAcceptRequest,
  onRejectRequest,
  onRemoveFriend,
  onFollow,
  onUnfollow,
  onBlock,
  onUnblock,
  onMessage,
  hideMessage = false,
}) => {
  if (!relationship || relationship.isOwnProfile) return null;

  const blockLoading = actionLoading.block || actionLoading.unblock;
  const friendLoading =
    actionLoading.add_friend ||
    actionLoading.cancel_request ||
    actionLoading.accept_request ||
    actionLoading.reject_request ||
    actionLoading.remove_friend;
  const followLoading = actionLoading.follow || actionLoading.unfollow;

  const confirmAndRun = async (message: string, operation: () => Promise<void>) => {
    if (!window.confirm(message)) return;
    await operation();
  };

  const runAction = (operation: Promise<void> | void) => {
    Promise.resolve(operation).catch(() => undefined);
  };

  return (
    <div className="relationship-actions">
      {actionError && (
        <Alert variant="danger" className="mb-2" role="alert">
          {actionError}
        </Alert>
      )}

      {relationship.blockedByCurrentUser ? (
        <Button
          type="button"
          variant="warning"
          disabled={blockLoading}
          onClick={() => relationship.block && runAction(onUnblock(relationship.block.id))}
          aria-label="Unblock user"
        >
          {actionLoading.unblock ? 'Unblocking...' : 'Unblock'}
        </Button>
      ) : (
        <>
          {relationship.friendState === 'none' && (
            <Button
              type="button"
              variant="primary"
              disabled={friendLoading}
              onClick={() => runAction(onAddFriend(targetUserId))}
            >
              {actionLoading.add_friend ? 'Sending...' : 'Add Friend'}
            </Button>
          )}

          {relationship.friendState === 'outgoing_pending' && relationship.outgoingRequest && (
            <Button
              type="button"
              variant="outline-secondary"
              disabled={friendLoading}
              onClick={() => runAction(onCancelRequest(relationship.outgoingRequest!.id))}
            >
              {actionLoading.cancel_request ? 'Canceling...' : 'Cancel Request'}
            </Button>
          )}

          {relationship.friendState === 'incoming_pending' && relationship.incomingRequest && (
            <>
              <Button
                type="button"
                variant="success"
                disabled={friendLoading}
                onClick={() => runAction(onAcceptRequest(relationship.incomingRequest!.id))}
              >
                {actionLoading.accept_request ? 'Accepting...' : 'Accept Request'}
              </Button>
              <Button
                type="button"
                variant="outline-secondary"
                disabled={friendLoading}
                onClick={() => runAction(onRejectRequest(relationship.incomingRequest!.id))}
              >
                {actionLoading.reject_request ? 'Rejecting...' : 'Reject Request'}
              </Button>
            </>
          )}

          {relationship.friendState === 'friends' && relationship.friendship && (
            <Button
              type="button"
              variant="outline-danger"
              disabled={friendLoading}
              onClick={() =>
                runAction(confirmAndRun('Remove this friend?', () => onRemoveFriend(relationship.friendship!.id)))
              }
            >
              {actionLoading.remove_friend ? 'Removing...' : 'Remove Friend'}
            </Button>
          )}

          {relationship.following && relationship.follow ? (
            <Button
              type="button"
              variant="outline-primary"
              disabled={followLoading}
              onClick={() => runAction(onUnfollow(relationship.follow!.id))}
            >
              {actionLoading.unfollow ? 'Unfollowing...' : 'Unfollow'}
            </Button>
          ) : (
            <Button
              type="button"
              variant="outline-primary"
              disabled={followLoading}
              onClick={() => runAction(onFollow(targetUserId))}
            >
              {actionLoading.follow ? 'Following...' : 'Follow'}
            </Button>
          )}

          {!hideMessage && relationship.canMessage && onMessage && (
            <Button type="button" variant="primary" onClick={onMessage}>
              Message
            </Button>
          )}

          <Button
            type="button"
            variant="outline-danger"
            disabled={blockLoading}
            onClick={() =>
              runAction(confirmAndRun(
                'Block this user? You can unblock them later from Friends.',
                () => onBlock(targetUserId)
              ))
            }
          >
            {actionLoading.block ? 'Blocking...' : 'Block'}
          </Button>
        </>
      )}
    </div>
  );
};

export default RelationshipActions;
