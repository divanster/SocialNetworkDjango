import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Posts from './Posts';

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: null }),
}));

jest.mock('../FeedItem/ReactionButton', () => () => <button type="button">React</button>);
jest.mock('../FeedItem/CommentSection', () => () => <div>Comments</div>);
jest.mock('./EditPostModal', () => () => null);

describe('Posts', () => {
  it('links post author identity to profile route when author id exists', () => {
    render(
      <MemoryRouter>
        <Posts
          posts={[
            {
              id: 'post-1',
              title: 'Post title',
              content: 'Post content',
              author: { id: 'author-1', username: 'authorUser' },
              created_at: '2026-10-09T10:00:00Z',
              updated_at: '2026-10-09T10:00:00Z',
            },
          ]}
          onDeletePost={() => undefined}
          onUpdatePost={() => undefined}
          deletingPostIds={[]}
          updatingPostIds={[]}
        />
      </MemoryRouter>
    );

    const authorLink = screen.getByRole('link', { name: 'authorUser' });
    expect(authorLink).toHaveAttribute('href', '/profile/author-1');
  });
});
