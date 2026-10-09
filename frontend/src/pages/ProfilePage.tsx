import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Alert, Button, Card, Col, Container, Form, Row, Spinner } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import { fetchProfileData, fetchUserById, updateProfileData, UserData } from '../services/api';
import Avatar from '../components/Common/Avatar';
import { buildMessengerPathForUser, hasValidUserId, profileBasePath } from '../utils/profileRoutes';
import { useSocialGraph } from '../hooks/useSocialGraph';
import RelationshipActions from '../components/Social/RelationshipActions';
import './ProfilePage.css';

type ProfileFormState = {
  username: string;
  first_name: string;
  last_name: string;
  bio: string;
  town: string;
  country: string;
  relationship_status: string;
  phone: string;
};

const defaultFormState: ProfileFormState = {
  username: '',
  first_name: '',
  last_name: '',
  bio: '',
  town: '',
  country: '',
  relationship_status: '',
  phone: '',
};

const ProfilePage: React.FC = () => {
  const { user: currentUser, setUser } = useAuth();
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();

  const [profileUser, setProfileUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<ProfileFormState>(defaultFormState);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const {
    actionError,
    actionLoading,
    deriveRelationship,
    addFriend,
    cancelOutgoingRequest,
    acceptIncomingRequest,
    rejectIncomingRequest,
    removeFriend,
    follow,
    unfollow,
    block,
    unblock,
    clearActionError,
  } = useSocialGraph();

  const viewedUserId = userId || currentUser?.id;
  const isOwnProfile = Boolean(currentUser?.id && profileUser?.id && currentUser.id === profileUser.id);

  const profileDisplayName = useMemo(() => {
    if (!profileUser) return '';
    const firstName = profileUser.profile?.first_name?.trim();
    const lastName = profileUser.profile?.last_name?.trim();
    const fullName = [firstName, lastName].filter(Boolean).join(' ').trim();
    return fullName || profileUser.full_name || profileUser.username;
  }, [profileUser]);
  const relationship = useMemo(
    () => (profileUser ? deriveRelationship(profileUser.id) : null),
    [deriveRelationship, profileUser]
  );

  const resetFormFromProfile = (value: UserData) => {
    setForm({
      username: value.username || '',
      first_name: value.profile?.first_name || '',
      last_name: value.profile?.last_name || '',
      bio: value.profile?.bio || '',
      town: value.profile?.town || '',
      country: value.profile?.country || '',
      relationship_status: value.profile?.relationship_status || '',
      phone: value.profile?.phone || '',
    });
  };

  const loadProfile = async () => {
    if (!currentUser) {
      setLoading(false);
      setErrorMessage('You must be logged in to view profiles.');
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    setNotFound(false);
    setSaveSuccess(null);
    clearActionError();
    try {
      const targetId = userId || currentUser.id;
      const data = targetId === currentUser.id
        ? await fetchProfileData()
        : await fetchUserById(targetId);

      if (!data) {
        setNotFound(true);
        setProfileUser(null);
        return;
      }
      setProfileUser(data);
    } catch (error: any) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        setNotFound(true);
      } else {
        setErrorMessage('Could not load this profile. Please retry.');
      }
      setProfileUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [currentUser?.id, userId]);

  useEffect(() => {
    if (!profileUser || !isOwnProfile) return;
    resetFormFromProfile(profileUser);
  }, [profileUser, isOwnProfile]);

  const handleInputChange = (field: keyof ProfileFormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setFieldErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const normalizeError = (value: unknown): string => {
    if (Array.isArray(value)) return value.map((item) => String(item)).join(', ');
    if (typeof value === 'string') return value;
    return 'Invalid value';
  };

  const applyServerValidationErrors = (responseData: any) => {
    const next: Record<string, string> = {};
    if (!responseData || typeof responseData !== 'object') {
      setFieldErrors(next);
      return;
    }

    if (responseData.username) next.username = normalizeError(responseData.username);
    if (responseData.profile && typeof responseData.profile === 'object') {
      const profileErrorEntries = Object.entries(responseData.profile);
      for (const [key, value] of profileErrorEntries) {
        next[key] = normalizeError(value);
      }
    }
    if (responseData.non_field_errors) {
      next.form = normalizeError(responseData.non_field_errors);
    }
    setFieldErrors(next);
  };

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!isOwnProfile) return;
    setSaving(true);
    setSaveSuccess(null);
    setErrorMessage(null);
    setFieldErrors({});

    const payload = {
      username: form.username.trim(),
      profile: {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        bio: form.bio.trim(),
        town: form.town.trim(),
        country: form.country.trim(),
        relationship_status: form.relationship_status.trim(),
        phone: form.phone.trim(),
      },
    };

    try {
      const updatedUser = await updateProfileData(payload);
      setProfileUser(updatedUser);
      setUser(updatedUser);
      setIsEditOpen(false);
      setSaveSuccess('Profile updated successfully.');
    } catch (error: any) {
      if (axios.isAxiosError(error) && error.response?.data) {
        applyServerValidationErrors(error.response.data);
      } else {
        setErrorMessage('Unable to save profile changes. Please retry.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleRetry = () => {
    loadProfile();
  };

  if (loading) {
    return (
      <Container className="profile-page py-4" aria-live="polite">
        <div className="profile-loading text-center">
          <Spinner animation="border" role="status" aria-label="Loading profile" />
          <p className="mt-2 mb-0">Loading profile...</p>
        </div>
      </Container>
    );
  }

  if (notFound || !profileUser || !hasValidUserId(viewedUserId)) {
    return (
      <Container className="profile-page py-4">
        <Card className="profile-state-card">
          <Card.Body>
            <h1 className="h4">Profile not found</h1>
            <p className="mb-3">The user profile you requested is unavailable.</p>
            <Button type="button" variant="primary" onClick={() => navigate('/')}>Go to Home</Button>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  return (
    <Container className="profile-page py-4">
      <Card className="profile-header-card mb-3">
        <div className="profile-cover" aria-hidden="true" />
        <Card.Body>
          <Row className="align-items-center g-3">
            <Col xs="auto">
              <Avatar
                size={96}
                src={profileUser.profile?.profile_picture || undefined}
                name={profileDisplayName}
                alt={`${profileDisplayName} avatar`}
                className="profile-avatar"
              />
            </Col>
            <Col>
              <h1 className="h3 mb-1">{profileDisplayName}</h1>
              <p className="profile-username mb-1">@{profileUser.username}</p>
              <span className={`profile-type-badge ${isOwnProfile ? 'own' : 'other'}`}>
                {isOwnProfile ? 'Your profile' : 'User profile'}
              </span>
            </Col>
            <Col xs={12} md="auto" className="profile-actions">
              {isOwnProfile ? (
                <Button
                  type="button"
                  variant="primary"
                  onClick={() => {
                    resetFormFromProfile(profileUser);
                    setIsEditOpen(true);
                  }}
                >
                  Edit Profile
                </Button>
              ) : (
                relationship && (
                  <RelationshipActions
                    relationship={relationship}
                    targetUserId={profileUser.id}
                    actionLoading={actionLoading}
                    actionError={actionError}
                    onAddFriend={addFriend}
                    onCancelRequest={cancelOutgoingRequest}
                    onAcceptRequest={acceptIncomingRequest}
                    onRejectRequest={rejectIncomingRequest}
                    onRemoveFriend={removeFriend}
                    onFollow={follow}
                    onUnfollow={unfollow}
                    onBlock={block}
                    onUnblock={unblock}
                    onMessage={() => navigate(buildMessengerPathForUser(profileUser.id))}
                  />
                )
              )}
              <Button type="button" variant="outline-secondary" onClick={() => navigate('/')}>
                Back to Home
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {saveSuccess && <Alert variant="success">{saveSuccess}</Alert>}
      {errorMessage && (
        <Alert variant="danger" role="alert" className="d-flex justify-content-between align-items-center gap-2">
          <span>{errorMessage}</span>
          <Button size="sm" variant="outline-danger" onClick={handleRetry}>Retry</Button>
        </Alert>
      )}

      <Row className="g-3">
        <Col xs={12} lg={7}>
          <Card className="profile-section-card">
            <Card.Body>
              <h2 className="h5">About</h2>
              <ul className="profile-details-list">
                {profileUser.profile?.bio && <li><strong>Bio:</strong> {profileUser.profile.bio}</li>}
                {profileUser.profile?.town && <li><strong>Town:</strong> {profileUser.profile.town}</li>}
                {profileUser.profile?.country && <li><strong>Country:</strong> {profileUser.profile.country}</li>}
                {isOwnProfile && profileUser.profile?.phone && <li><strong>Phone:</strong> {profileUser.profile.phone}</li>}
                {profileUser.profile?.relationship_status && (
                  <li><strong>Relationship status:</strong> {profileUser.profile.relationship_status}</li>
                )}
              </ul>
              {!profileUser.profile?.bio &&
                !profileUser.profile?.town &&
                !profileUser.profile?.country &&
                !(isOwnProfile && profileUser.profile?.phone) &&
                !profileUser.profile?.relationship_status && (
                <p className="text-muted mb-0">No profile details available yet.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12} lg={5}>
          <Card className="profile-section-card">
            <Card.Body>
              <h2 className="h5">Content</h2>
              <p className="text-muted mb-0">
                User-scoped content endpoints for posts, albums, and stories are not currently available in the API.
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {isEditOpen && isOwnProfile && (
        <div className="profile-edit-overlay" role="dialog" aria-modal="true" aria-labelledby="edit-profile-title">
          <Card className="profile-edit-card">
            <Card.Body>
              <h2 id="edit-profile-title" className="h5 mb-3">Edit Profile</h2>
              {fieldErrors.form && <Alert variant="danger">{fieldErrors.form}</Alert>}
              <Form onSubmit={handleSave}>
                <Form.Group className="mb-2" controlId="profile-username">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    isInvalid={Boolean(fieldErrors.username)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.username}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-first-name">
                  <Form.Label>First name</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.first_name}
                    onChange={(e) => handleInputChange('first_name', e.target.value)}
                    isInvalid={Boolean(fieldErrors.first_name)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.first_name}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-last-name">
                  <Form.Label>Last name</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.last_name}
                    onChange={(e) => handleInputChange('last_name', e.target.value)}
                    isInvalid={Boolean(fieldErrors.last_name)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.last_name}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-bio">
                  <Form.Label>Bio</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={form.bio}
                    onChange={(e) => handleInputChange('bio', e.target.value)}
                    isInvalid={Boolean(fieldErrors.bio)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.bio}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-town">
                  <Form.Label>Town</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.town}
                    onChange={(e) => handleInputChange('town', e.target.value)}
                    isInvalid={Boolean(fieldErrors.town)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.town}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-country">
                  <Form.Label>Country</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.country}
                    onChange={(e) => handleInputChange('country', e.target.value)}
                    isInvalid={Boolean(fieldErrors.country)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.country}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-2" controlId="profile-relationship">
                  <Form.Label>Relationship status</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.relationship_status}
                    onChange={(e) => handleInputChange('relationship_status', e.target.value)}
                    isInvalid={Boolean(fieldErrors.relationship_status)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.relationship_status}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group className="mb-3" controlId="profile-phone">
                  <Form.Label>Phone</Form.Label>
                  <Form.Control
                    type="text"
                    value={form.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    isInvalid={Boolean(fieldErrors.phone)}
                  />
                  <Form.Control.Feedback type="invalid">{fieldErrors.phone}</Form.Control.Feedback>
                </Form.Group>

                <div className="d-flex justify-content-end gap-2">
                  <Button
                    type="button"
                    variant="outline-secondary"
                    onClick={() => {
                      setIsEditOpen(false);
                      setFieldErrors({});
                      resetFormFromProfile(profileUser);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary" disabled={saving}>
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </div>
      )}

      {!isOwnProfile && (
        <div className="profile-own-link-row">
          <Button type="button" onClick={() => navigate(profileBasePath)} variant="link">Go to my profile</Button>
        </div>
      )}
    </Container>
  );
};

export default ProfilePage;
