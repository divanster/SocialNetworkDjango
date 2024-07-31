import React, { useEffect, useState } from 'react';
import {
    fetchNewsFeed,
    fetchAlbums
} from '../services/api';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import CreatePost from '../components/CentralNewsFeed/CreatePost';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';
import { Container, Row, Col } from 'react-bootstrap';
import './NewsFeed.css';

const NewsFeed: React.FC = () => {
    const [posts, setPosts] = useState<any[]>([]);
    const [albums, setAlbums] = useState<any[]>([]);

    useEffect(() => {
        const getNewsFeedData = async () => {
            try {
                const postsData = await fetchNewsFeed();
                console.log('Posts data:', postsData);
                setPosts(postsData.posts || []);

                const albumsData = await fetchAlbums();
                console.log('Albums data:', albumsData);
                setAlbums(Array.isArray(albumsData.albums) ? albumsData.albums : []);
            } catch (error) {
                console.error('Error fetching news feed data:', error);
            }
        };

        getNewsFeedData();
    }, []);

    return (
        <Container fluid>
            <Row>
                <Col xs={12} md={3} className="left-sidebar">
                    <Profile />
                </Col>
                <Col xs={12} md={6} className="central-news-feed">
                    <CreatePost />
                    <CreateAlbum />
                    {posts.length > 0 ? <Posts posts={posts} /> : <p>No posts available</p>}
                    {Array.isArray(albums) && albums.length > 0 ? albums.map(album => (
                        <Album key={album.id} album={album} />
                    )) : <p>No albums available</p>}
                </Col>
                <Col xs={12} md={3} className="right-sidebar">
                    <FriendRequests />
                    <Birthdays />
                    <Contacts />
                </Col>
            </Row>
        </Container>
    );
};

export default NewsFeed;
