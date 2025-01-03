# SocialNetworkDjango

**A feature-rich social networking application built with Django, React, GraphQL, Kafka, and Celery, offering real-time messaging, notifications, and seamless user interactions.**

![SocialNetworkDjango Banner](https://your-banner-image-url.com/banner.png) <!-- Replace with your actual banner image URL -->

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using Docker](#using-docker)
  - [Manual Setup](#manual-setup)
- [Running the Application](#running-the-application)
  - [With Docker Compose](#with-docker-compose)
  - [Without Docker](#without-docker)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

---

## Features

- **User Authentication:** Secure registration, login, and logout using JWT.
- **Social Interactions:**
  - Create, edit, and delete posts.
  - Follow and unfollow users.
  - Like and comment on posts.
- **Real-Time Communication:**
  - Real-time messaging between users via WebSockets.
  - Instant notifications for events like new messages, comments, and likes.
- **Media Management:** Upload and manage images for posts and user profiles.
- **Event-Driven Architecture:**
  - Kafka integration for efficient event handling.
  - Celery for asynchronous task processing.
- **API Documentation:**
  - Comprehensive GraphQL API using Graphene.
  - REST API documentation with Swagger UI.
- **Security:**
  - Implemented Content Security Policy (CSP).
  - Robust security settings for production environments.
- **CI/CD:** Automated workflows with GitHub Actions for continuous integration and deployment.

---

## Technology Stack

- **Backend:**
  - Django
  - Django REST Framework
  - GraphQL (Graphene Django)
  - Channels (WebSockets)
  - Celery
  - Kafka
  - PostgreSQL
  - Redis
- **Frontend:**
  - React
  - Redux
  - Bootstrap
  - React Router
- **DevOps:**
  - Docker & Docker Compose
  - GitHub Actions
- **Others:**
  - Sentry for error tracking
  - Elasticsearch (optional, commented out in settings)
  - Twilio (optional, commented out in settings)
  - FCM for push notifications (optional, commented out in settings)

---

## Prerequisites

Ensure you have the following installed on your machine:

- **Operating System:** macOS, Linux, or Windows.
- **Docker:** [Install Docker](https://www.docker.com/get-started)
- **Docker Compose:** Comes bundled with Docker Desktop.
- **Git:** [Install Git](https://git-scm.com/downloads)

*Note: The project is configured for `linux/arm64` architecture. Ensure your Docker setup supports this architecture.*

---

## Installation

### Using Docker

Docker simplifies the setup by containerizing all services.

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/SocialNetworkDjango.git
   cd SocialNetworkDjango
   ```

2. **Create Environment Variables:**

   Duplicate the `.env.example` file:

   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` with your configurations.

3. **Build and Start Services:**

   ```bash
   docker-compose up --build
   ```

4. **Services Included:**

   - `db`: PostgreSQL database.
   - `redis`: Redis server for caching and Celery broker.
   - `zookeeper` & `kafka`: Kafka setup for event handling.
   - `web`: Django backend (ASGI) with Uvicorn.
   - `celery-worker`: Celery worker for async tasks.
   - `kafka-consumer`: Kafka consumer service.
   - `frontend`: React frontend.

5. **Access the Application:**

   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
   - **GraphQL Playground:** [http://localhost:8000/graphql](http://localhost:8000/graphql)
   - **API Documentation:** [http://localhost:8000/schema/swagger-ui/](http://localhost:8000/schema/swagger-ui/)

### Manual Setup

For those preferring a non-Docker setup:

#### Backend Setup

1. Navigate to Backend Directory:

   ```bash
   cd backend
   ```

2. Create and Activate Virtual Environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements.dev.txt
   ```

4. Configure Environment Variables:

   ```bash
   cp .env.example .env
   ```

   Edit `backend/.env` with your settings.

5. Apply Migrations:

   ```bash
   python manage.py migrate
   ```

6. Run the Development Server:

   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. Navigate to Frontend Directory:

   ```bash
   cd frontend
   ```

2. Install Dependencies:

   ```bash
   npm install
   ```

3. Configure Environment Variables:

   Create a `.env` file in the frontend directory:

   ```env
   REACT_APP_API_URL=http://localhost:8000/api/v1
   REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
   CHOKIDAR_USEPOLLING=true
   NODE_OPTIONS=--openssl-legacy-provider
   ```

4. Start the Development Server:

   ```bash
   npm start
   ```

---

## Running the Application

### With Docker Compose

Ensure all services are up and running:

```bash
docker-compose up --build
```

Detach Mode: Run containers in the background.

```bash
docker-compose up --build -d
```

### Without Docker

#### Backend

1. Activate Virtual Environment:

   ```bash
   source backend/venv/bin/activate
   ```

2. Run Django Server:

   ```bash
   python manage.py runserver
   ```

#### Celery Worker

In a separate terminal:

```bash
source backend/venv/bin/activate
celery -A config worker --loglevel=info
```

#### Kafka Consumer

In another terminal:

```bash
source backend/venv/bin/activate
python manage.py run_kafka_consumer
```

#### Frontend

1. Navigate to Frontend Directory:

   ```bash
   cd frontend
   ```

2. Start React Server:

   ```bash
   npm start
   ```

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web,backend

# Database Settings
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
DB_HOST=db
DB_PORT=5432

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka Settings
KAFKA_BROKER_URL=kafka:9092
KAFKA_CONSUMER_GROUP_ID=centralized_consumer_group
KAFKA_TOPICS=social-events:social-events,newsfeed-events:newsfeed-events
KAFKA_ENCRYPTION_KEY=your-kafka-encryption-key

# Celery Settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Sentry Settings
SENTRY_DSN=your-sentry-dsn

# Other Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://frontend:3000
```

### Frontend (`frontend/.env`)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
CHOKIDAR_USEPOLLING=true
NODE_OPTIONS=--openssl-legacy-provider
```

Ensure you replace placeholder values with your actual configurations.

---

## API Documentation

### GraphQL Playground

Interact with the GraphQL API:

- **URL:** [http://localhost:8000/graphql](http://localhost:8000/graphql)

### REST API Documentation

View REST API endpoints via Swagger UI:

- **URL:** [http://localhost:8000/schema/swagger-ui/](http://localhost:8000/schema/swagger-ui/)

---

## Running Tests

### Backend Tests

Execute Django's test suite:

```bash
cd backend
source venv/bin/activate
python manage.py test
```

Ensure all tests pass before deploying or merging changes.

---

## Deployment

To deploy the application to a production environment:

1. **Set `DEBUG=False`:** Update your environment variables to set `DEBUG=False`.

2. **Configure Allowed Hosts:** Appropriately set the `ALLOWED_HOSTS` variable.

3. **Use a Production-Ready Web Server:** Deploy with Gunicorn or Daphne.

4. **Secure Environment Variables:** Utilize Docker secrets or environment managers.

5. **Enable HTTPS:** Set up SSL certificates for secure communication.

6. **Monitor with Sentry:** Ensure Sentry is active for error tracking.

7. **Use a Process Manager:** Manage Celery workers and other services with Supervisor or systemd.

8. **Scale Services:** Adjust Kafka brokers, Celery workers, and other services based on load.

Refer to the Django Deployment Checklist for detailed guidelines.

---

## Contributing

Contributions are welcome! Follow these steps to contribute:

1. **Fork the Repository:**

   Click the "Fork" button on the repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/yourusername/SocialNetworkDjango.git
   cd SocialNetworkDjango
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Changes and Commit:**

   ```bash
   git add .
   git commit -m "Add some feature"
   ```

5. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Create a Pull Request:**

   Navigate to your fork on GitHub and click "Compare & pull request."

Ensure your code follows the project's coding standards and includes relevant tests.

---

## License

This project is licensed under the MIT License.

---

## Contact

For inquiries or support, reach out to [divanster@mail.com].

---

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [React](https://reactjs.org/)
- [GraphQL](https://graphql.org/)
- [Kafka](https://kafka.apache.org/)
- [Celery](https://celeryproject.org/)
- [Docker](https://www.docker.com/)
- [Sentry](https://sentry.io/)
- [Bootstrap](https://getbootstrap.com/)
- [GitHub Actions](https://github.com/features/actions)

---

**Notes:**

1. **Banner Image:** Replace `https://your-banner-image-url.com/banner.png` with the actual URL of your project's banner image to enhance visual appeal.

2. **Repository URL:** Ensure the clone command points to your actual GitHub repository.

3. **Environment Variables:** Carefully set all necessary environment variables in both `backend/.env` and `frontend/.env` files. Avoid committing sensitive information to version control.

4. **Optional Services:** If utilizing services like Elasticsearch, Twilio, or FCM for push notifications, uncomment and configure the relevant sections in `settings.py` and `docker-compose.yml` as needed.

5. **Docker Architecture:** The `docker-compose.yml` is tailored for `linux/arm64` architecture. Adjust the platform settings if deploying on a different architecture.

6. **Health Checks:** Docker Compose includes health checks to ensure all services are operational before starting dependent services. Monitor these to troubleshoot any startup issues.

7. **Security Settings:** The `settings.py` is configured with robust security measures for production. Ensure `DEBUG` is set to `False` and all security settings are appropriately configured when deploying.

8. **Testing:** Regularly run your test suites to maintain code quality and catch issues early.

9. **Continuous Integration:** Leverage GitHub Actions to automate testing, building, and deployment processes, ensuring a smooth CI/CD pipeline.

10. **WebSocket Management:** Implement proper cleanup and reconnection logic in your frontend to handle WebSocket connections efficiently, as detailed in your `useWebSocket` hook logs.



