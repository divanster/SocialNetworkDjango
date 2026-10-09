import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import StoryCarousel from './StoryCarousel';
import { deleteStory } from '../../services/contentService';

jest.mock('../../services/contentService', () => ({
  deleteStory: jest.fn(),
}));

let mockCurrentUserId = 'u-1';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: mockCurrentUserId } }),
}));

const mockedDeleteStory = deleteStory as jest.MockedFunction<typeof deleteStory>;

describe('StoryCarousel', () => {
  beforeEach(() => {
    mockCurrentUserId = 'u-1';
    mockedDeleteStory.mockResolvedValue();
    window.confirm = jest.fn().mockReturnValue(true);
  });

  it('opens story viewer and links owner identity', async () => {
    render(
      <MemoryRouter>
        <StoryCarousel
          stories={[
            {
              id: 's-1',
              user: { id: 'u-1', full_name: 'Owner Name', profile_picture: '' },
              content: 'story content',
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ]}
        />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /Open story by Owner Name/i }));
    const profileLinks = await screen.findAllByRole('link', { name: /Open Owner Name profile/i });
    expect(profileLinks.some((link) => link.getAttribute('href') === '/profile/u-1')).toBe(true);
  });

  it('shows delete only for owner and calls delete endpoint', async () => {
    const onDeleted = jest.fn();
    render(
      <MemoryRouter>
        <StoryCarousel
          stories={[
            {
              id: 's-1',
              user: { id: 'u-1', full_name: 'Owner Name', profile_picture: '' },
              content: 'story content',
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ]}
          onStoryDeleted={onDeleted}
        />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /Open story by Owner Name/i }));
    fireEvent.click(await screen.findByRole('button', { name: 'Delete' }));

    await waitFor(() => expect(mockedDeleteStory).toHaveBeenCalledWith('s-1'));
    expect(onDeleted).toHaveBeenCalledWith('s-1');
  });

  it('hides delete action for non-owner story', async () => {
    mockCurrentUserId = 'u-2';

    render(
      <MemoryRouter>
        <StoryCarousel
          stories={[
            {
              id: 's-9',
              user: { id: 'u-1', full_name: 'Owner Name', profile_picture: '' },
              content: 'story content',
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ]}
        />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /Open story by Owner Name/i }));
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Delete' })).not.toBeInTheDocument());
  });
});
