import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup } from '../../services/auth';
import { Form, Button, Card } from 'react-bootstrap';

const Signup: React.FC = () => {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [gender, setGender] = useState('N');
    const [bio, setBio] = useState('');
    const [phone, setPhone] = useState('');
    const [town, setTown] = useState('');
    const [country, setCountry] = useState('');
    const [profilePicture, setProfilePicture] = useState<File | null>(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setProfilePicture(e.target.files[0]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        const formData = new FormData();
        formData.append('email', email);
        formData.append('username', username);
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);
        formData.append('first_name', firstName);
        formData.append('last_name', lastName);
        formData.append('date_of_birth', dateOfBirth);
        formData.append('gender', gender);
        formData.append('bio', bio);
        formData.append('phone', phone);
        formData.append('town', town);
        formData.append('country', country);
        if (profilePicture) {
            formData.append('profile_picture', profilePicture);
        }

        try {
            await signup(formData);
            navigate('/login');
        } catch (err) {
            setError('Error creating account');
        }
    };

    return (
        <Card className="my-5 p-3 border-primary">
            <Card.Body>
                <Form onSubmit={handleSubmit} encType="multipart/form-data">
                    <h2>Signup</h2>
                    {error && <p className="text-danger">{error}</p>}
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Email address</Form.Label>
                        <Form.Control
                            type="email"
                            placeholder="Enter email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </Form.Group>

                    <Form.Group controlId="formBasicUsername">
                        <Form.Label>Username</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </Form.Group>

                    <Form.Group controlId="formBasicPassword">
                        <Form.Label>Password</Form.Label>
                        <Form.Control
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </Form.Group>

                    <Form.Group controlId="formBasicConfirmPassword">
                        <Form.Label>Confirm Password</Form.Label>
                        <Form.Control
                            type="password"
                            placeholder="Confirm Password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </Form.Group>

                    <Form.Group controlId="formFirstName">
                        <Form.Label>First Name</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="First Name"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formLastName">
                        <Form.Label>Last Name</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formDateOfBirth">
                        <Form.Label>Date of Birth</Form.Label>
                        <Form.Control
                            type="date"
                            value={dateOfBirth}
                            onChange={(e) => setDateOfBirth(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formGender">
                        <Form.Label>Gender</Form.Label>
                        <Form.Control
                            as="select"
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                        >
                            <option value="N">Not specified</option>
                            <option value="M">Male</option>
                            <option value="F">Female</option>
                        </Form.Control>
                    </Form.Group>

                    <Form.Group controlId="formBio">
                        <Form.Label>Bio</Form.Label>
                        <Form.Control
                            as="textarea"
                            placeholder="Tell us about yourself"
                            value={bio}
                            onChange={(e) => setBio(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formPhone">
                        <Form.Label>Phone</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Phone"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formTown">
                        <Form.Label>Town</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Town"
                            value={town}
                            onChange={(e) => setTown(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formCountry">
                        <Form.Label>Country</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Country"
                            value={country}
                            onChange={(e) => setCountry(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formProfilePicture">
                        <Form.Label>Profile Picture</Form.Label>
                        <Form.Control
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                        />
                    </Form.Group>

                    <Button variant="primary" type="submit">
                        Signup
                    </Button>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default Signup;
