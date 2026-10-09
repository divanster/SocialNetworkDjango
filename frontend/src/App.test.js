import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

jest.mock('./components/Navbar/Navbar', () => () => <div>Navbar</div>);
jest.mock('./components/ProtectedRoute', () => ({ children }) => <>{children}</>);
jest.mock('./pages/NewsFeed', () => () => <div>NewsFeed Page</div>);
jest.mock('./pages/Messenger', () => () => <div>Messenger Page</div>);
jest.mock('./pages/ProfilePage', () => () => <div>Profile Page</div>);
jest.mock('./pages/FriendsPage', () => () => <div>Friends Page</div>);
jest.mock('./pages/Albums', () => () => <div>Albums Page</div>);
jest.mock('./pages/AlbumDetailPage', () => () => <div>Album Detail Page</div>);
jest.mock('./components/Auth/Login', () => () => <div>Login Page</div>);
jest.mock('./components/Auth/Signup', () => () => <div>Signup Page</div>);
jest.mock('./components/NotFound', () => () => <div>Not Found</div>);

test('renders login route content', async () => {
  render(
    <MemoryRouter initialEntries={['/login']}>
      <App />
    </MemoryRouter>
  );
  expect(await screen.findByText('Login Page')).toBeInTheDocument();
  expect(screen.getByText('Navbar')).toBeInTheDocument();
});

test('renders friends route content', async () => {
  render(
    <MemoryRouter initialEntries={['/friends']}>
      <App />
    </MemoryRouter>
  );
  expect(await screen.findByText('Friends Page')).toBeInTheDocument();
});

test('renders albums route content', async () => {
  render(
    <MemoryRouter initialEntries={['/albums']}>
      <App />
    </MemoryRouter>
  );
  expect(await screen.findByText('Albums Page')).toBeInTheDocument();
});
