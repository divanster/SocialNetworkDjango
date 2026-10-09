import React from 'react';
import axios from 'axios';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SearchBar from './SearchBar';

jest.mock('axios');

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ token: 'token' }),
}));

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('SearchBar', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockedAxios.get.mockResolvedValue({
      data: {
        users: [],
        posts: [],
        albums: [{ id: 'album-9', title: 'Vacation' }],
        stories: [],
      },
    } as any);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.resetAllMocks();
  });

  it('routes album search result to /albums/:id', async () => {
    render(
      <MemoryRouter>
        <SearchBar />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Search users, posts, albums, stories/i), {
      target: { value: 'vac' },
    });

    await act(async () => {
      jest.advanceTimersByTime(350);
    });

    const link = await screen.findByRole('link', { name: 'Vacation' });
    expect(link).toHaveAttribute('href', '/albums/album-9');
  });
});
