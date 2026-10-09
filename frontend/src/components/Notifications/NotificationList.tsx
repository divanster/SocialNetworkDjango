import React from 'react';
import { Alert, Badge, Button, ListGroup, Spinner } from 'react-bootstrap';
import UserIdentityLink from '../Common/UserIdentityLink';
import { NotificationItem } from '../../services/notificationsService';
import { NotificationDestination } from '../../utils/notificationDestinationResolver';
import './NotificationList.css';

interface NotificationListProps {
  notifications: NotificationItem[];
  loading: boolean;
  error: string | null;
  compact?: boolean;
  onRetry: () => void;
  onSelect: (notification: NotificationItem, destination: NotificationDestination) => void;
  onMarkAllRead?: () => void;
  canMarkAllRead?: boolean;
  resolveDestination: (notification: NotificationItem) => NotificationDestination;
}

const NotificationList: React.FC<NotificationListProps> = ({
  notifications,
  loading,
  error,
  compact = false,
  onRetry,
  onSelect,
  onMarkAllRead,
  canMarkAllRead = false,
  resolveDestination,
}) => {
  return (
    <div className="notification-list">
      <div className="notification-list__controls">
        {canMarkAllRead && onMarkAllRead && (
          <Button variant="link" size="sm" onClick={onMarkAllRead}>
            Mark all as read
          </Button>
        )}
      </div>

      {loading ? (
        <div className="py-2 px-2">
          <Spinner animation="border" size="sm" className="me-2" />
          Loading notifications...
        </div>
      ) : error ? (
        <Alert variant="danger" className="mb-2 d-flex justify-content-between align-items-center">
          <span>{error}</span>
          <Button size="sm" variant="outline-danger" onClick={onRetry}>
            Retry
          </Button>
        </Alert>
      ) : notifications.length === 0 ? (
        <Alert variant="light" className="mb-0">No notifications yet.</Alert>
      ) : (
        <ListGroup variant={compact ? 'flush' : undefined}>
          {notifications.map((notification) => {
            const destination = resolveDestination(notification);
            const senderName = notification.sender_username || 'Someone';
            return (
              <ListGroup.Item
                key={notification.id}
                action
                className={`notification-item ${notification.read ? 'notification-read' : 'notification-unread'}`}
                onClick={() => onSelect(notification, destination)}
                aria-label={notification.read ? 'Read notification' : 'Unread notification'}
              >
                <div className="d-flex align-items-start justify-content-between gap-2">
                  <div>
                    <div className="notification-sender">
                      {notification.sender_id ? (
                        <UserIdentityLink
                          userId={notification.sender_id}
                          onClick={(event) => event.stopPropagation()}
                        >
                          {senderName}
                        </UserIdentityLink>
                      ) : (
                        <span>{senderName}</span>
                      )}
                    </div>
                    <div>{notification.text}</div>
                    <small className="text-muted">{new Date(notification.created_at).toLocaleString()}</small>
                    {!destination.canNavigate && (
                      <small className="d-block text-muted">No direct destination</small>
                    )}
                  </div>
                  {!notification.read && <Badge bg="primary">Unread</Badge>}
                </div>
              </ListGroup.Item>
            );
          })}
        </ListGroup>
      )}
    </div>
  );
};

export default NotificationList;
