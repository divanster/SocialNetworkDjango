import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import AlbumDetailPage from './AlbumDetailPage';
import * as contentService from '../services/contentService';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 'me-1' } }),
}));

describe('AlbumDetailPage', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('loads album detail by route id', async () => {
    jest.spyOn(contentService, 'getAlbumById').mockResolvedValue({
      id: 'alb-1',
      user_id: 'me-1',
      title: 'Trip',
      description: 'Trip photos',
      visibility: 'public',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
      photos: [],
      tags: [],
      author: { id: 'me-1', username: 'me', email: 'me@example.com', full_name: 'Me' },
    } as any);
    jest.spyOn(contentService, 'listPhotos').mockResolvedValue([]);

    render(
      <MemoryRouter initialEntries={['/albums/alb-1']}>
        <Routes>
          <Route path="/albums/:albumId" element={<AlbumDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: 'Trip' })).toBeInTheDocument();
  });

  it('shows not found state for invalid album', async () => {
    jest.spyOn(contentService, 'getAlbumById').mockRejectedValue({ response: { status: 404 } });
    jest.spyOn(contentService, 'listPhotos').mockResolvedValue([]);

    render(
      <MemoryRouter initialEntries={['/albums/missing']}>
        <Routes>
          <Route path="/albums/:albumId" element={<AlbumDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Album not found or unavailable/i)).toBeInTheDocument());
  });
});
