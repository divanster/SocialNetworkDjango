import React, { useEffect, useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  },
});

const Profile: React.FC = () => {
  const [profileData, setProfileData] = useState<any>({});
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    gender: 'N',
    dateOfBirth: '',
    bio: '',
    phone: '',
    town: '',
    country: '',
    relationshipStatus: 'S',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch user profile data
    const fetchProfileData = async () => {
      try {
        const response = await axios.get(`${API_URL}/users/users/me/`, getHeaders());
        setProfileData(response.data);
        setFormData({
          firstName: response.data.first_name || '',
          lastName: response.data.last_name || '',
          gender: response.data.gender || 'N',
          dateOfBirth: response.data.date_of_birth || '',
          bio: response.data.bio || '',
          phone: response.data.phone || '',
          town: response.data.town || '',
          country: response.data.country || '',
          relationshipStatus: response.data.relationship_status || 'S',
        });
      } catch (err) {
        if (axios.isAxiosError(err)) {
          console.error('Axios error:', err.response || err.message);
          setError(`Failed to fetch profile data: ${err.message}`);
        } else {
          console.error('Unexpected error:', err);
          setError('An unexpected error occurred.');
        }
      }
    };

    fetchProfileData();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setProfilePicture(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const updateData = new FormData();
    updateData.append('first_name', formData.firstName);
    updateData.append('last_name', formData.lastName);
    updateData.append('gender', formData.gender);
    updateData.append('date_of_birth', formData.dateOfBirth);
    updateData.append('bio', formData.bio);
    updateData.append('phone', formData.phone);
    updateData.append('town', formData.town);
    updateData.append('country', formData.country);
    updateData.append('relationship_status', formData.relationshipStatus);

    if (profilePicture) {
      updateData.append('profile_picture', profilePicture);
    }

    try {
      const response = await axios.patch(`${API_URL}/users/users/me/`, updateData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setProfileData(response.data);
      alert('Profile updated successfully!');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.error('Failed to update profile:', err.response || err.message);
        setError(`Failed to update profile: ${err.message}`);
      } else {
        console.error('Unexpected error:', err);
        setError('An unexpected error occurred.');
      }
    }
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="profile">
      <img
        src={profileData.profile_picture ? `http://127.0.0.1:8000${profileData.profile_picture}` : '/static/default_images/default_profile.jpg'}
        alt="Profileeeeeee"
        className="img-fluid rounded-circle"
      />
      <h3>{profileData.username || 'Your Name'}</h3>
      <Form onSubmit={handleSubmit} encType="multipart/form-data">
        <Form.Group controlId="formFirstName">
          <Form.Label>First Name</Form.Label>
          <Form.Control
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formLastName">
          <Form.Label>Last Name</Form.Label>
          <Form.Control
            type="text"
            name="lastName"
            value={formData.lastName}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formGender">
          <Form.Label>Gender</Form.Label>
          <Form.Control
            as="select"
            name="gender"
            value={formData.gender}
            onChange={handleInputChange}
          >
            <option value="N">Not specified</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </Form.Control>
        </Form.Group>

        <Form.Group controlId="formDateOfBirth">
          <Form.Label>Date of Birth</Form.Label>
          <Form.Control
            type="date"
            name="dateOfBirth"
            value={formData.dateOfBirth}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formBio">
          <Form.Label>Bio</Form.Label>
          <Form.Control
            as="textarea"
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formPhone">
          <Form.Label>Phone</Form.Label>
          <Form.Control
            type="text"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formTown">
          <Form.Label>Town</Form.Label>
          <Form.Control
            type="text"
            name="town"
            value={formData.town}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formCountry">
          <Form.Label>Country</Form.Label>
          <Form.Control
            type="text"
            name="country"
            value={formData.country}
            onChange={handleInputChange}
          />
        </Form.Group>

        <Form.Group controlId="formRelationshipStatus">
          <Form.Label>Relationship Status</Form.Label>
          <Form.Control
            as="select"
            name="relationshipStatus"
            value={formData.relationshipStatus}
            onChange={handleInputChange}
          >
            <option value="S">Single</option>
            <option value="M">Married</option>
            <option value="D">Divorced</option>
            <option value="W">Widowed</option>
            <option value="P">In a relationship</option>
            <option value="C">Complicated</option>
          </Form.Control>
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
          Update Profile
        </Button>
      </Form>
    </div>
  );
};

export default Profile;
