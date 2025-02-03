import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './SearchBar.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any>({ users: [], posts: [], albums: [], stories: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const fetchSearchResults = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults({ users: [], posts: [], albums: [], stories: [] });
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/search/`, {
        params: { query: searchQuery },
      });
      setResults(response.data);
      setShowDropdown(true);
    } catch (error) {
      console.error('Error fetching search results:', error);
      setResults({ users: [], posts: [], albums: [], stories: [] });
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

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search users, posts, albums, stories..."
        value={query}
        onChange={handleChange}
        onFocus={() => {
          if (results.users.length > 0 || results.posts.length > 0 || results.albums.length > 0 || results.stories.length > 0) {
            setShowDropdown(true);
          }
        }}
      />
      {isLoading && <div className="loader"></div>}
      {showDropdown && (results.users.length > 0 || results.posts.length > 0 || results.albums.length > 0 || results.stories.length > 0) && (
        <ul className="search-dropdown">
          {results.users.map((user: any) => (
            <li key={user.id}>
              <Link to={`/profile/${user.id}`} onClick={() => setShowDropdown(false)}>
                <strong>{user.username}</strong>
              </Link>
            </li>
          ))}
          {results.posts.map((post: any) => (
            <li key={post.id}>
              <Link to={`/post/${post.id}`} onClick={() => setShowDropdown(false)}>
                <strong>{post.title}</strong>
              </Link>
            </li>
          ))}
          {results.albums.map((album: any) => (
            <li key={album.id}>
              <Link to={`/album/${album.id}`} onClick={() => setShowDropdown(false)}>
                <strong>{album.title}</strong>
              </Link>
            </li>
          ))}
          {results.stories.map((story: any) => (
            <li key={story.id}>
              <Link to={`/story/${story.id}`} onClick={() => setShowDropdown(false)}>
                <strong>{story.title}</strong>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
