import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ChatWindow from './ChatWindow';

let socketHandler: ((payload: any) => void) | null = null;
const mockUser = { id: 'me-1' };

const mockFetchMessages = jest.fn();
const mockMarkMessageAsRead = jest.fn();
const mockSendMessageToUser = jest.fn();
const mockTransformMessage = jest.fn();

jest.mock('../../services/messagesService', () => ({
  fetchMessages: (...args: any[]) => mockFetchMessages(...args),
  markMessageAsRead: (...args: any[]) => mockMarkMessageAsRead(...args),
  sendMessageToUser: (...args: any[]) => mockSendMessageToUser(...args),
  transformMessage: (...args: any[]) => mockTransformMessage(...args),
}));

jest.mock('../../hooks/useWebSocket', () => ({
  __esModule: true,
  default: (_group: string, handlers: any) => {
    socketHandler = handlers.onMessage;
    return { sendMessage: jest.fn() };
  },
}));

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
  }),
}));

jest.mock('../../contexts/OnlineStatusContext', () => ({
  useOnlineStatus: () => ({
    onlineUsers: ['friend-1'],
  }),
}));

jest.mock('../Common/Avatar', () => () => <span>Avatar</span>);

describe('ChatWindow', () => {
  beforeEach(() => {
    socketHandler = null;
    mockFetchMessages.mockResolvedValue([
      {
        id: 'm-1',
        sender: { id: 'friend-1', username: 'f1', full_name: 'Friend One', profile_picture: null },
        receiver: { id: 'me-1', username: 'me', full_name: 'Me', profile_picture: null },
        content: 'hello',
        read: false,
        created_at: '2026-01-01T00:00:00Z',
      },
    ]);
    mockMarkMessageAsRead.mockResolvedValue(undefined);
    mockSendMessageToUser.mockResolvedValue({
      id: 'm-2',
      sender: { id: 'me-1', username: 'me', full_name: 'Me', profile_picture: null },
      receiver: { id: 'friend-1', username: 'f1', full_name: 'Friend One', profile_picture: null },
      content: 'sent',
      read: false,
      created_at: '2026-01-01T00:05:00Z',
    });
    mockTransformMessage.mockImplementation((raw) => ({
      id: raw.id,
      sender: { id: raw.sender, username: raw.sender_name, full_name: raw.sender_full_name, profile_picture: null },
      receiver: { id: raw.receiver, username: raw.receiver_name, full_name: raw.receiver_full_name, profile_picture: null },
      content: raw.content,
      read: raw.read,
      created_at: raw.created_at,
    }));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders REST conversation history', async () => {
    render(
      <MemoryRouter>
        <ChatWindow friendId="friend-1" friendName="Friend One" />
      </MemoryRouter>
    );

    expect(await screen.findByText('hello')).toBeInTheDocument();
    expect(mockMarkMessageAsRead).toHaveBeenCalledWith('m-1');
    expect(screen.getByRole('link', { name: 'Friend One' })).toHaveAttribute('href', '/profile/friend-1');
  });

  it('does not send empty messages', async () => {
    render(
      <MemoryRouter>
        <ChatWindow friendId="friend-1" friendName="Friend One" />
      </MemoryRouter>
    );

    await screen.findByText('hello');
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();
  });

  it('sends valid message with canonical payload', async () => {
    render(
      <MemoryRouter>
        <ChatWindow friendId="friend-1" friendName="Friend One" />
      </MemoryRouter>
    );

    await screen.findByText('hello');
    fireEvent.change(screen.getByLabelText('Message text'), { target: { value: 'sent' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send' }));
    await waitFor(() => expect(mockSendMessageToUser).toHaveBeenCalledWith('friend-1', 'sent'));
  });

  it('deduplicates realtime messages by id', async () => {
    render(
      <MemoryRouter>
        <ChatWindow friendId="friend-1" friendName="Friend One" />
      </MemoryRouter>
    );

    await screen.findByText('hello');

    const realtimePayload = {
      type: 'messenger.message',
      data: {
        id: 'm-3',
        sender: 'friend-1',
        receiver: 'me-1',
        sender_name: 'friend-1',
        receiver_name: 'me-1',
        sender_full_name: 'Friend One',
        receiver_full_name: 'Me',
        content: 'realtime',
        read: false,
        created_at: '2026-01-01T00:10:00Z',
      },
    };

    await act(async () => {
      socketHandler?.(realtimePayload);
      socketHandler?.(realtimePayload);
    });

    await waitFor(() => expect(screen.getAllByText('realtime')).toHaveLength(1));
  });
});
