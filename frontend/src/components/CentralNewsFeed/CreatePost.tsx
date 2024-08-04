import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/posts';

const CreatePost: React.FC = () => {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [images, setImages] = useState<FileList | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('title', title);
        formData.append('content', content);
        if (images) {
            for (let i = 0; i < images.length; i++) {
                formData.append('image_files', images[i]);
            }
        }

        try {
            const token = localStorage.getItem('token');
            console.log('Token:', token); // Log token
            const response = await axios.post(`${API_URL}/posts/`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log('Response data:', response.data);
            // Handle successful post creation
            setTitle('');
            setContent('');
            setImages(null);
            setError(null);
        } catch (error) {
            console.error('Error creating post:', error);
            if (axios.isAxiosError(error)) {
                console.error('Response Error:', error.response); // Log error response
                setError(error.response?.data?.detail || 'An error occurred');
            } else {
                setError('An unexpected error occurred');
            }
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
            {error && <div className="alert alert-danger">{error}</div>}
            <Form.Group>
                <Form.Label>Title</Form.Label>
                <Form.Control
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Content</Form.Label>
                <Form.Control
                    as="textarea"
                    rows={3}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Upload Images</Form.Label>
                <Form.Control
                    type="file"
                    multiple
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                        if (e.target.files) setImages(e.target.files);
                    }}
                />
            </Form.Group>
            <Button type="submit">Post</Button>
        </Form>
    );
};

export default CreatePost;
