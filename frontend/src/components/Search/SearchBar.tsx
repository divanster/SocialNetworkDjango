import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './SearchBar.css';
import { useAuth } from '../../contexts/AuthContext';
import { buildAlbumPath, buildProfilePath } from '../../utils/profileRoutes';
import { API_URL } from '../../services/api';

interface SearchResults {
  users: { id: string; username: string }[];
  albums: { id: string; title: string }[];
  posts: unknown[];
  stories: unknown[];
}

const SearchBar: React.FC = () => {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResults>({ users: [], posts: [], albums: [], stories: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);

  const hasResults = results.users.length > 0 || results.albums.length > 0;

  const fetchSearchResults = async (searchQuery: string) => {
    if (!token || !searchQuery.trim()) {
      setResults({ users: [], posts: [], albums: [], stories: [] });
      setShowDropdown(false);
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/search/`, {
        params: { query: searchQuery },
      });
      const payload = response.data ?? {};
      const normalized: SearchResults = {
        users: Array.isArray(payload.users) ? payload.users : [],
        albums: Array.isArray(payload.albums) ? payload.albums : [],
        posts: Array.isArray(payload.posts) ? payload.posts : [],
        stories: Array.isArray(payload.stories) ? payload.stories : [],
      };
      setResults(normalized);
      setShowDropdown(normalized.users.length > 0 || normalized.albums.length > 0);
    } catch (error) {
      setResults({ users: [], posts: [], albums: [], stories: [] });
      setShowDropdown(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);

    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      fetchSearchResults(value);
    }, 300); // Debounce by 300ms
  };

  useEffect(() => () => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
  }, []);

  useEffect(() => {
    const handleOutside = (event: MouseEvent) => {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    return () => {
      document.removeEventListener('mousedown', handleOutside);
    };
  }, []);

  return (
    <div className="search-bar" ref={wrapperRef}>
      <input
        type="text"
        placeholder="Search users, posts, albums, stories..."
        value={query}
        onChange={handleChange}
        aria-label="Search users and albums"
        onKeyDown={(event) => {
          if (event.key === 'Escape') {
            setShowDropdown(false);
          }
        }}
        onFocus={() => {
          if (hasResults) {
            setShowDropdown(true);
          }
        }}
      />
      {isLoading && <div className="loader"></div>}
      {showDropdown && hasResults && (
        <ul className="search-dropdown">
          {results.users.map((user) => (
            <li key={user.id}>
              <Link to={buildProfilePath(String(user.id))} onClick={() => setShowDropdown(false)}>
                <strong>{user.username}</strong>
              </Link>
            </li>
          ))}
          {results.albums.map((album) => (
            <li key={album.id}>
              <Link to={buildAlbumPath(String(album.id))} onClick={() => setShowDropdown(false)}>
                <strong>{album.title}</strong>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
