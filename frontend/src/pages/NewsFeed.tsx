// frontend/src/pages/NewsFeed.tsx
import React, { useEffect, useState } from 'react';
import fetchNewsFeed from '../services/api';
import Posts from '../components/CentralNewsFeed/Posts';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import { Container, Row, Col, Card } from 'react-bootstrap';

const NewsFeed: React.FC = () => {
    const [feed, setFeed] = useState<any>({ posts: [], comments: [], reactions: [], albums: [], stories: [] });

    useEffect(() => {
        const fetchData = async () => {
            const data = await fetchNewsFeed();
            setFeed(data);
        };
        fetchData();
    }, []);

    return (
        <Container fluid>
            <Row>
                <Col md={3}>
                    <Profile />
                </Col>
                <Col md={6}>
                    <Card className="mb-4 p-3">
                        <Posts posts={feed.posts} />
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="mb-4 p-3">
                        <FriendRequests />
                    </Card>
                    <Card className="mb-4 p-3">
                        <Birthdays />
                    </Card>
                    <Card className="mb-4 p-3">
                        <Contacts />
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default NewsFeed;
