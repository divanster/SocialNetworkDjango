import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import axios from 'axios';
import ProfilePage from './ProfilePage';
import { fetchProfileData, fetchUserById, updateProfileData } from '../services/api';

const mockNavigate = jest.fn();
const mockSetUser = jest.fn();

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../services/api', () => ({
  ...jest.requireActual('../services/api'),
  fetchProfileData: jest.fn(),
  fetchUserById: jest.fn(),
  updateProfileData: jest.fn(),
}));

jest.mock('../hooks/useSocialGraph', () => ({
  useSocialGraph: jest.fn(),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const { useAuth } = jest.requireMock('../contexts/AuthContext') as { useAuth: jest.Mock };
const { useSocialGraph } = jest.requireMock('../hooks/useSocialGraph') as { useSocialGraph: jest.Mock };

const makeSocialGraphMock = (overrides: Partial<any> = {}) => ({
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
  deriveRelationship: jest.fn(() => ({
    isOwnProfile: false,
    friendState: 'none',
    following: false,
    blockedByCurrentUser: false,
    blockedByOtherUserKnown: false,
    blockedByOtherUser: false,
    canMessage: true,
  })),
  addFriend: jest.fn().mockResolvedValue(undefined),
  cancelOutgoingRequest: jest.fn().mockResolvedValue(undefined),
  acceptIncomingRequest: jest.fn().mockResolvedValue(undefined),
  rejectIncomingRequest: jest.fn().mockResolvedValue(undefined),
  removeFriend: jest.fn().mockResolvedValue(undefined),
  follow: jest.fn().mockResolvedValue(undefined),
  unfollow: jest.fn().mockResolvedValue(undefined),
  block: jest.fn().mockResolvedValue(undefined),
  unblock: jest.fn().mockResolvedValue(undefined),
  clearActionError: jest.fn(),
  ...overrides,
});

const currentUser = {
  id: 'user-1',
  email: 'user1@example.com',
  username: 'user1',
  full_name: 'User One',
  profile: {
    first_name: 'User',
    last_name: 'One',
    bio: 'My bio',
    town: 'Sofia',
    country: 'BG',
    relationship_status: 'S',
    phone: '',
    profile_picture: null,
  },
};

const otherUser = {
  id: 'user-2',
  email: 'user2@example.com',
  username: 'user2',
  full_name: 'User Two',
  profile: {
    first_name: 'User',
    last_name: 'Two',
    bio: '',
    town: '',
    country: '',
    relationship_status: '',
    phone: '',
    profile_picture: null,
  },
};

const renderProfilePage = (initialEntry: string) => {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/" element={<div>Home page</div>} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/profile/:userId" element={<ProfilePage />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('ProfilePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuth.mockReturnValue({
      user: currentUser,
      setUser: mockSetUser,
    });
    (axios.isAxiosError as unknown as jest.Mock).mockImplementation(
      (value: unknown) => Boolean((value as any)?.response)
    );
    useSocialGraph.mockReturnValue(makeSocialGraphMock());
  });

  it('loads own profile and shows edit action', async () => {
    (fetchProfileData as jest.Mock).mockResolvedValue(currentUser);

    renderProfilePage('/profile');

    expect(await screen.findByText('User One')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Edit Profile' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Add Friend' })).not.toBeInTheDocument();
  });

  it('loads another user by route id and hides edit action', async () => {
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');

    expect(await screen.findByText('User Two')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Edit Profile' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Message' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add Friend' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Follow' })).toBeInTheDocument();
  });

  it('does not show edit action on another user profile', async () => {
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');

    await screen.findByText('User Two');
    expect(screen.queryByRole('button', { name: 'Edit Profile' })).not.toBeInTheDocument();
  });

  it('renders not found state for invalid user', async () => {
    (fetchUserById as jest.Mock).mockRejectedValue({ response: { status: 404 } });

    renderProfilePage('/profile/not-valid');

    expect(await screen.findByText('Profile not found')).toBeInTheDocument();
  });

  it('submits edit profile with patch payload and updates auth user', async () => {
    (fetchProfileData as jest.Mock).mockResolvedValue(currentUser);
    const updated = {
      ...currentUser,
      username: 'new-user1',
      profile: { ...currentUser.profile, bio: 'Updated bio' },
    };
    (updateProfileData as jest.Mock).mockResolvedValue(updated);

    renderProfilePage('/profile');

    await screen.findByText('User One');
    fireEvent.click(screen.getByRole('button', { name: 'Edit Profile' }));
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'new-user1' } });
    fireEvent.change(screen.getByLabelText('Bio'), { target: { value: 'Updated bio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => {
      expect(updateProfileData).toHaveBeenCalledWith(
        expect.objectContaining({
          username: 'new-user1',
          profile: expect.objectContaining({ bio: 'Updated bio' }),
        })
      );
    });
    expect(mockSetUser).toHaveBeenCalledWith(updated);
  });

  it('navigates to messenger with selected participant from message action', async () => {
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');

    await screen.findByText('User Two');
    fireEvent.click(screen.getByRole('button', { name: 'Message' }));

    expect(mockNavigate).toHaveBeenCalledWith('/messenger?userId=user-2');
  });

  it('renders outgoing pending state for other profile', async () => {
    useSocialGraph.mockReturnValue(
      makeSocialGraphMock({
        deriveRelationship: jest.fn(() => ({
          isOwnProfile: false,
          friendState: 'outgoing_pending',
          following: false,
          blockedByCurrentUser: false,
          blockedByOtherUserKnown: false,
          blockedByOtherUser: false,
          canMessage: true,
          outgoingRequest: { id: 'req-1' },
        })),
      })
    );
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');
    await screen.findByText('User Two');
    expect(screen.getByRole('button', { name: 'Cancel Request' })).toBeInTheDocument();
  });

  it('renders incoming request state with accept and reject', async () => {
    useSocialGraph.mockReturnValue(
      makeSocialGraphMock({
        deriveRelationship: jest.fn(() => ({
          isOwnProfile: false,
          friendState: 'incoming_pending',
          following: false,
          blockedByCurrentUser: false,
          blockedByOtherUserKnown: false,
          blockedByOtherUser: false,
          canMessage: true,
          incomingRequest: { id: 'req-2' },
        })),
      })
    );
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');
    await screen.findByText('User Two');
    expect(screen.getByRole('button', { name: 'Accept Request' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reject Request' })).toBeInTheDocument();
  });

  it('renders friend state with remove friend action', async () => {
    useSocialGraph.mockReturnValue(
      makeSocialGraphMock({
        deriveRelationship: jest.fn(() => ({
          isOwnProfile: false,
          friendState: 'friends',
          following: true,
          blockedByCurrentUser: false,
          blockedByOtherUserKnown: false,
          blockedByOtherUser: false,
          canMessage: true,
          friendship: { id: 'friendship-1' },
          follow: { id: 'follow-1' },
        })),
      })
    );
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');
    await screen.findByText('User Two');
    expect(screen.getByRole('button', { name: 'Remove Friend' })).toBeInTheDocument();
  });

  it('hides interaction controls when blocked and shows unblock', async () => {
    useSocialGraph.mockReturnValue(
      makeSocialGraphMock({
        deriveRelationship: jest.fn(() => ({
          isOwnProfile: false,
          friendState: 'none',
          following: false,
          blockedByCurrentUser: true,
          blockedByOtherUserKnown: false,
          blockedByOtherUser: false,
          canMessage: false,
          block: { id: 'block-1' },
        })),
      })
    );
    (fetchUserById as jest.Mock).mockResolvedValue(otherUser);

    renderProfilePage('/profile/user-2');
    await screen.findByText('User Two');
    expect(screen.getByRole('button', { name: 'Unblock user' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Message' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Add Friend' })).not.toBeInTheDocument();
  });
});
