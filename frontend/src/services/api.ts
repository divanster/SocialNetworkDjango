// frontend/src/services/api.ts
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const fetchNewsFeed = async () => {
    try {
        const response = await axios.get(`${API_URL}/feed/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching news feed', error);
        return { posts: [], comments: [], reactions: [], albums: [], stories: [] };
    }
};

export default fetchNewsFeed;
