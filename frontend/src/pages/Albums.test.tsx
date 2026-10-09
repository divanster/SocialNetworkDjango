import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Albums from './Albums';
import * as contentService from '../services/contentService';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'me-1' },
  }),
}));

jest.mock('../components/CentralNewsFeed/CreateAlbum', () => ({ onAlbumCreated }: any) => (
  <button type="button" onClick={() => onAlbumCreated({ id: 'a-new', user_id: 'me-1', title: 'New', description: 'D', visibility: 'public', created_at: '', updated_at: '', photos: [], tags: [], author: { id: 'me-1', username: 'me', email: '', full_name: 'Me' } })}>
    Mock Create Album
  </button>
));

jest.mock('../components/FeedItem/Album', () => ({ album }: any) => <div>{album.title}</div>);

describe('Albums page', () => {
  beforeEach(() => {
    jest.spyOn(contentService, 'listAlbums').mockResolvedValue([
      {
        id: 'a-1',
        user_id: 'me-1',
        title: 'Album One',
        description: 'Desc',
        visibility: 'public',
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
        photos: [],
        tags: [],
        author: { id: 'me-1', username: 'me', email: 'me@example.com', full_name: 'Me' },
      } as any,
    ]);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders album list from API', async () => {
    render(
      <MemoryRouter>
        <Albums />
      </MemoryRouter>
    );

    expect(await screen.findByText('Album One')).toBeInTheDocument();
  });

  it('shows empty state when no albums are returned', async () => {
    jest.spyOn(contentService, 'listAlbums').mockResolvedValueOnce([]);
    render(
      <MemoryRouter>
        <Albums />
      </MemoryRouter>
    );
    expect(await screen.findByText('No albums yet')).toBeInTheDocument();
  });

  it('adds newly created album to the list', async () => {
    render(
      <MemoryRouter>
        <Albums />
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole('button', { name: 'Mock Create Album' }));
    await waitFor(() => expect(screen.getByText('New')).toBeInTheDocument());
  });
});
