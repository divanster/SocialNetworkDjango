// frontend/src/components/Search/SearchBar.tsx

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './SearchBar.css';
import { useAuth } from '../../contexts/AuthContext';

interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const SearchBar: React.FC = () => {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const fetchSearchResults = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/users/search/`, {
        params: { query: searchQuery },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setResults(response.data);
      setShowDropdown(true);
    } catch (error) {
      console.error('Error fetching search results:', error);
      setResults([]);
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
    <div className="search-bar" ref={searchRef}>
      <input
        type="text"
        placeholder="Search users..."
        value={query}
        onChange={handleChange}
        onFocus={() => {
          if (results.length > 0) setShowDropdown(true);
        }}
      />
      {isLoading && <div className="loader"></div>}
      {showDropdown && results.length > 0 && (
        <ul className="search-dropdown">
          {results.map((user) => (
            <li key={user.id}>
              <Link to={`/profile/${user.id}`} onClick={() => setShowDropdown(false)}>
                <img src={user.profile_picture} alt={`${user.username}'s profile`} />
                <div>
                  <strong>{user.full_name}</strong>
                  <span>@{user.username}</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
