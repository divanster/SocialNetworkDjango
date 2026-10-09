import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import CreatePosting from './CreatePosting';
import axios from 'axios';
import { createStory } from '../../services/contentService';

jest.mock('axios');
jest.mock('../../services/contentService', () => ({
  createStory: jest.fn(),
}));

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    token: 'token',
    user: { username: 'tester', profile: { profile_picture: null } },
  }),
}));

jest.mock('../Common/UserTagPicker', () => () => <div>Tag Picker</div>);

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedCreateStory = createStory as jest.MockedFunction<typeof createStory>;

describe('CreatePosting', () => {
  beforeEach(() => {
    Object.defineProperty(URL, 'createObjectURL', {
      writable: true,
      value: jest.fn(() => 'blob:preview'),
    });
    Object.defineProperty(URL, 'revokeObjectURL', {
      writable: true,
      value: jest.fn(),
    });
    mockedAxios.post.mockResolvedValue({ data: { id: 'post-1', content: 'Hello' } } as any);
    mockedCreateStory.mockResolvedValue({} as any);
  });

  it('shows and removes selected image preview before posting', async () => {
    render(
      <MemoryRouter>
        <CreatePosting
          onPostCreated={() => undefined}
          onAlbumCreated={() => undefined}
          sendMessage={() => undefined}
          sendAlbumMessage={() => undefined}
        />
      </MemoryRouter>
    );

    const imageInput = screen.getByLabelText('Photo') as HTMLInputElement;
    const file = new File(['image'], 'preview.png', { type: 'image/png' });
    fireEvent.change(imageInput, { target: { files: [file] } });

    expect(await screen.findByAltText('attachment-0')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /remove preview\.png/i }));
    await waitFor(() => expect(screen.queryByAltText('attachment-0')).not.toBeInTheDocument());
  });

  it('submits story as FormData payload', async () => {
    render(
      <MemoryRouter>
        <CreatePosting
          onPostCreated={() => undefined}
          onAlbumCreated={() => undefined}
          sendMessage={() => undefined}
          sendAlbumMessage={() => undefined}
        />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /story/i }));
    fireEvent.change(screen.getByPlaceholderText('Share a quick update'), { target: { value: 'My story' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create Story' }));

    await waitFor(() => expect(mockedCreateStory).toHaveBeenCalledTimes(1));
    expect(mockedCreateStory.mock.calls[0][0]).toBeInstanceOf(FormData);
  });
});
