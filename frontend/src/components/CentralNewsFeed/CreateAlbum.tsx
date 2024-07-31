import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

const CreateAlbum: React.FC = () => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [photos, setPhotos] = useState<FileList | null>(null);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', description);
        if (photos) {
            Array.from(photos).forEach(photo => {
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
        } catch (error) {
            console.error('Error creating album:', error);
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
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
