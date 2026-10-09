import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Messenger from './Messenger';
import { fetchUserById } from '../services/api';

jest.mock('../services/api', () => ({
  fetchUserById: jest.fn(),
}));

jest.mock('../components/Messenger/ContactsSidebar', () => ({ onSelectFriend }: any) => (
  <button
    type="button"
    onClick={() => onSelectFriend({ id: 'friend-2', username: 'friend2', full_name: 'Friend Two', profile_picture: null })}
  >
    Select Friend
  </button>
));

jest.mock('../components/Messenger/ChatWindow', () => ({ friendId }: any) => <div>Chat for {friendId}</div>);

const mockedFetchUserById = fetchUserById as jest.MockedFunction<typeof fetchUserById>;

describe('Messenger page', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('restores selected participant from query userId', async () => {
    mockedFetchUserById.mockResolvedValue({
      id: 'friend-1',
      username: 'friend1',
      full_name: 'Friend One',
      profile: { first_name: '', last_name: '', profile_picture: null },
    } as any);

    render(
      <MemoryRouter initialEntries={['/messenger?userId=friend-1']}>
        <Routes>
          <Route path="/messenger" element={<Messenger />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Chat for friend-1')).toBeInTheDocument();
  });

  it('shows recoverable state for invalid query userId', async () => {
    mockedFetchUserById.mockRejectedValue(new Error('Not found'));

    render(
      <MemoryRouter initialEntries={['/messenger?userId=missing']}>
        <Routes>
          <Route path="/messenger" element={<Messenger />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText(/Could not open this conversation/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Choose contact' }));
    await waitFor(() => expect(screen.getByText(/Select a contact to start chatting/i)).toBeInTheDocument());
  });
});
