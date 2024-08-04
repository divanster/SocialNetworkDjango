import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

const CreateAlbum: React.FC = () => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [photos, setPhotos] = useState<FileList | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', description);

        if (photos) {
            Array.from(photos).forEach((photo) => {
                formData.append('photos_upload', photo);
            });
        }

        try {
            const response = await axios.post('http://localhost:8000/api/albums/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
            });
            console.log('Album created successfully:', response.data);
            setTitle('');
            setDescription('');
            setPhotos(null);
            setSuccess('Album created successfully!');
        } catch (error) {
            console.error('Error creating album:', error);
            if (axios.isAxiosError(error)) {
                setError(error.response?.data?.detail || 'An error occurred while creating the album.');
            } else {
                setError('An unexpected error occurred.');
            }
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <Form.Group>
                <Form.Label>Title</Form.Label>
                <Form.Control
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Description</Form.Label>
                <Form.Control
                    as="textarea"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Upload Photos</Form.Label>
                <Form.Control
                    type="file"
                    multiple
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                        if (e.target.files) {
                            setPhotos(e.target.files);
                        }
                    }}
                />
            </Form.Group>
            <Button type="submit">Create Album</Button>
        </Form>
    );
};

export default CreateAlbum;
