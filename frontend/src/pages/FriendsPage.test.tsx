import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import FriendsPage from './FriendsPage';
import { fetchUserSuggestions, searchUsers } from '../services/socialGraphService';

const mockNavigate = jest.fn();
const mockRefresh = jest.fn();
const mockAccept = jest.fn().mockResolvedValue(undefined);
const mockReject = jest.fn().mockResolvedValue(undefined);
const mockRemoveFriend = jest.fn().mockResolvedValue(undefined);
const mockUnblock = jest.fn().mockResolvedValue(undefined);

jest.mock('../hooks/useSocialGraph', () => ({
  useSocialGraph: jest.fn(),
}));

jest.mock('../services/socialGraphService', () => ({
  ...jest.requireActual('../services/socialGraphService'),
  fetchUserSuggestions: jest.fn(),
  searchUsers: jest.fn(),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const { useSocialGraph } = jest.requireMock('../hooks/useSocialGraph') as { useSocialGraph: jest.Mock };

const createHookValue = () => ({
  currentUserId: 'me',
  friendRequests: [
    {
      id: 'incoming-1',
      sender: { id: 'u2', username: 'u2', full_name: 'User Two', profile_picture: null },
      receiver: { id: 'me', username: 'me', full_name: 'Me', profile_picture: null },
      status: 'pending',
      created_at: '',
    },
  ],
  friendships: [
    {
      id: 'friendship-1',
      user1: { id: 'me', username: 'me', full_name: 'Me', profile_picture: null },
      user2: { id: 'u3', username: 'u3', full_name: 'User Three', profile_picture: null },
      created_at: '',
    },
  ],
  blocks: [
    {
      id: 'block-1',
      blocker: { id: 'me', username: 'me', full_name: 'Me', profile_picture: null },
      blocked: { id: 'u4', username: 'u4', full_name: 'User Four', profile_picture: null },
      created_at: '',
    },
  ],
  loading: false,
  error: null,
  actionError: null,
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
  refresh: mockRefresh,
  deriveRelationship: jest.fn((id: string) => ({
    isOwnProfile: false,
    friendState: id === 'u3' ? 'friends' : id === 'u2' ? 'incoming_pending' : 'none',
    following: false,
    blockedByCurrentUser: id === 'u4',
    blockedByOtherUserKnown: false,
    blockedByOtherUser: false,
    canMessage: id !== 'u4',
    incomingRequest: id === 'u2' ? { id: 'incoming-1' } : undefined,
    friendship: id === 'u3' ? { id: 'friendship-1' } : undefined,
    block: id === 'u4' ? { id: 'block-1' } : undefined,
  })),
  addFriend: jest.fn().mockResolvedValue(undefined),
  cancelOutgoingRequest: jest.fn().mockResolvedValue(undefined),
  acceptIncomingRequest: mockAccept,
  rejectIncomingRequest: mockReject,
  removeFriend: mockRemoveFriend,
  follow: jest.fn().mockResolvedValue(undefined),
  unfollow: jest.fn().mockResolvedValue(undefined),
  block: jest.fn().mockResolvedValue(undefined),
  unblock: mockUnblock,
});

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={['/friends']}>
      <Routes>
        <Route path="/friends" element={<FriendsPage />} />
      </Routes>
    </MemoryRouter>
  );

describe('FriendsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useSocialGraph.mockReturnValue(createHookValue());
    (fetchUserSuggestions as jest.Mock).mockResolvedValue([
      { id: 'u5', username: 'u5', full_name: 'User Five', profile_picture: null },
    ]);
    (searchUsers as jest.Mock).mockResolvedValue([
      { id: 'u6', username: 'u6', full_name: 'User Six', profile_picture: null },
    ]);
  });

  it('renders friends, incoming requests, suggestions and blocked users sections', async () => {
    renderPage();

    expect(await screen.findByText('Current friends')).toBeInTheDocument();
    expect(screen.getByText('Incoming requests')).toBeInTheDocument();
    expect(screen.getByText('Suggestions')).toBeInTheDocument();
    expect(screen.getByText('Blocked users')).toBeInTheDocument();
    expect(screen.getByText('User Three')).toBeInTheDocument();
    expect(screen.getByText('User Two')).toBeInTheDocument();
    expect(screen.getByText('User Four')).toBeInTheDocument();
  });

  it('calls accept/reject handlers for incoming requests', async () => {
    renderPage();
    await screen.findByText('User Two');
    fireEvent.click(screen.getByRole('button', { name: 'Accept Request' }));
    expect(mockAccept).toHaveBeenCalledWith('incoming-1');
  });

  it('calls remove friend action from friends list', async () => {
    renderPage();
    await screen.findByText('User Three');
    (window.confirm as any) = jest.fn(() => true);
    fireEvent.click(screen.getByRole('button', { name: 'Remove Friend' }));
    expect(mockRemoveFriend).toHaveBeenCalledWith('friendship-1');
  });

  it('calls unblock action in blocked users section', async () => {
    renderPage();
    await screen.findByText('User Four');
    (window.confirm as any) = jest.fn(() => true);
    fireEvent.click(screen.getByRole('button', { name: 'Unblock' }));
    expect(mockUnblock).toHaveBeenCalledWith('block-1');
  });

  it('renders retry control on API failure', async () => {
    useSocialGraph.mockReturnValue({ ...createHookValue(), error: 'Failed to load data.' });
    renderPage();
    const retryButton = await screen.findByRole('button', { name: 'Retry' });
    fireEvent.click(retryButton);
    expect(mockRefresh).toHaveBeenCalled();
  });

  it('renders empty states', async () => {
    useSocialGraph.mockReturnValue({
      ...createHookValue(),
      friendRequests: [],
      friendships: [],
      blocks: [],
    });
    (fetchUserSuggestions as jest.Mock).mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText('You have no friends yet.')).toBeInTheDocument();
    expect(screen.getByText('No incoming requests.')).toBeInTheDocument();
    expect(screen.getByText('No outgoing pending requests.')).toBeInTheDocument();
    expect(await screen.findByText('No suggestions available right now.')).toBeInTheDocument();
    expect(screen.getByText('You have not blocked anyone.')).toBeInTheDocument();
  });
});
