import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import RelationshipActions from './RelationshipActions';
import { RelationshipState } from '../../hooks/useSocialGraph';

const createProps = (overrides: Partial<any> = {}) => ({
  relationship: {
    isOwnProfile: false,
    friendState: 'none',
    following: false,
    blockedByCurrentUser: false,
    blockedByOtherUserKnown: false,
    blockedByOtherUser: false,
    canMessage: true,
  } as RelationshipState,
  targetUserId: 'target-1',
  actionLoading: {
    add_friend: false,
    cancel_request: false,
    accept_request: false,
    reject_request: false,
    remove_friend: false,
    follow: false,
    unfollow: false,
    block: false,
    unblock: false,
  },
  actionError: null,
  onAddFriend: jest.fn().mockResolvedValue(undefined),
  onCancelRequest: jest.fn().mockResolvedValue(undefined),
  onAcceptRequest: jest.fn().mockResolvedValue(undefined),
  onRejectRequest: jest.fn().mockResolvedValue(undefined),
  onRemoveFriend: jest.fn().mockResolvedValue(undefined),
  onFollow: jest.fn().mockResolvedValue(undefined),
  onUnfollow: jest.fn().mockResolvedValue(undefined),
  onBlock: jest.fn().mockResolvedValue(undefined),
  onUnblock: jest.fn().mockResolvedValue(undefined),
  onMessage: jest.fn(),
  ...overrides,
});

describe('RelationshipActions', () => {
  beforeEach(() => {
    (window.confirm as any) = jest.fn(() => true);
  });

  it('shows Add Friend and Follow when there is no relationship', () => {
    render(<RelationshipActions {...createProps()} />);
    expect(screen.getByRole('button', { name: 'Add Friend' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Follow' })).toBeInTheDocument();
  });

  it('calls add friend callback with target user id', () => {
    const props = createProps();
    render(<RelationshipActions {...props} />);
    fireEvent.click(screen.getByRole('button', { name: 'Add Friend' }));
    expect(props.onAddFriend).toHaveBeenCalledWith('target-1');
  });

  it('renders outgoing pending state', () => {
    render(
      <RelationshipActions
        {...createProps({
          relationship: {
            isOwnProfile: false,
            friendState: 'outgoing_pending',
            following: false,
            blockedByCurrentUser: false,
            blockedByOtherUserKnown: false,
            blockedByOtherUser: false,
            canMessage: true,
            outgoingRequest: { id: 'request-1' },
          } as RelationshipState,
        })}
      />
    );
    expect(screen.getByRole('button', { name: 'Cancel Request' })).toBeInTheDocument();
  });

  it('renders incoming state with accept and reject', () => {
    render(
      <RelationshipActions
        {...createProps({
          relationship: {
            isOwnProfile: false,
            friendState: 'incoming_pending',
            following: false,
            blockedByCurrentUser: false,
            blockedByOtherUserKnown: false,
            blockedByOtherUser: false,
            canMessage: true,
            incomingRequest: { id: 'request-2' },
          } as RelationshipState,
        })}
      />
    );
    expect(screen.getByRole('button', { name: 'Accept Request' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reject Request' })).toBeInTheDocument();
  });

  it('renders friend state with remove friend', () => {
    render(
      <RelationshipActions
        {...createProps({
          relationship: {
            isOwnProfile: false,
            friendState: 'friends',
            following: false,
            blockedByCurrentUser: false,
            blockedByOtherUserKnown: false,
            blockedByOtherUser: false,
            canMessage: true,
            friendship: { id: 'friendship-1' },
          } as RelationshipState,
        })}
      />
    );
    expect(screen.getByRole('button', { name: 'Remove Friend' })).toBeInTheDocument();
  });

  it('calls follow and unfollow handlers', () => {
    const followProps = createProps();
    render(<RelationshipActions {...followProps} />);
    fireEvent.click(screen.getByRole('button', { name: 'Follow' }));
    expect(followProps.onFollow).toHaveBeenCalledWith('target-1');
  });

  it('hides message and friend/follow controls when blocked, shows unblock', () => {
    render(
      <RelationshipActions
        {...createProps({
          relationship: {
            isOwnProfile: false,
            friendState: 'none',
            following: false,
            blockedByCurrentUser: true,
            blockedByOtherUserKnown: false,
            blockedByOtherUser: false,
            canMessage: false,
            block: { id: 'block-1' },
          } as RelationshipState,
        })}
      />
    );
    expect(screen.getByRole('button', { name: 'Unblock user' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Add Friend' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Follow' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Message' })).not.toBeInTheDocument();
  });

  it('shows no actions on own profile', () => {
    render(
      <RelationshipActions
        {...createProps({
          relationship: {
            isOwnProfile: true,
            friendState: 'none',
            following: false,
            blockedByCurrentUser: false,
            blockedByOtherUserKnown: false,
            blockedByOtherUser: false,
            canMessage: false,
          } as RelationshipState,
        })}
      />
    );
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
