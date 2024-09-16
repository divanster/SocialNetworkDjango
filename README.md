SocialNetworkDjango Documentation  Project Technologies Documentation
This document provides an overview of all the technologies integrated into the project. It explains what each technology is, its purpose, and how it contributes to the project's functionality.

Table of Contents
1. Python and Django
2. django-environ
3. Django REST Framework (DRF)
4. Simple JWT
5. Djoser
6. CORS Headers
7. Django Channels
8. django-extensions
9. drf-spectacular
10. Custom Django Apps
11. django-celery-beat
12. Celery
13. Redis
14. WhiteNoise
15. Sentry SDK
16. PostgreSQL
17. Email Backend (SMTP with Gmail)
18. Logging Configuration
19. Security Enhancements
20. Caching
21. Error Tracking
22. Testing Utilities

Python and Django
* Python: A high-level, interpreted programming language known for its readability and versatility.
* Django: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
Usage in Project:
* Provides the foundational framework for building the web application.
* Enables rapid development with built-in functionalities for database interaction, user authentication, and more.

django-environ
* Purpose: Simplifies the management of environment variables in Django projects.
* Usage:
    * Reads environment variables from a .env file.
    * Helps in keeping sensitive information like secret keys and database passwords out of the codebase.
Benefits:
* Enhances security by avoiding hardcoding sensitive information.
* Makes configuration flexible across different environments (development, testing, production).

Django REST Framework (DRF)
* Purpose: A toolkit for building Web APIs with Django.
* Usage:
    * Provides serializers for converting complex data types to JSON.
    * Offers views and viewsets for handling API requests.
    * Includes built-in authentication and permission classes.
Features:
* Serialization: Easily convert model instances to and from JSON.
* Authentication: Supports various authentication methods.
* Throttling and Pagination: Controls request rates and paginates responses.

Simple JWT
* Purpose: Implements JSON Web Token (JWT) authentication for DRF.
* Usage:
    * Secures API endpoints by requiring JWTs for authentication.
    * Issues and validates tokens during user authentication processes.
Features:
* Token Rotation: Enhances security by rotating refresh tokens.
* Blacklisting: Invalidates tokens after logout or expiration.
* Customizable: Configurable token lifetimes and algorithms.

Djoser
* Purpose: Provides a set of views to handle basic actions like registration, login, logout, password reset, and account activation.
* Usage:
    * Simplifies the implementation of user authentication endpoints.
    * Works seamlessly with DRF and Simple JWT.
Features:
* Email Notifications: Sends emails for account activation and password resets.
* Customizable Serializers: Allows for custom user models and fields.
* Token Management: Integrates with JWT for token-based authentication.

CORS Headers
* Package: django-cors-headers
* Purpose: Handles Cross-Origin Resource Sharing (CORS) in Django applications.
* Usage:
    * Allows the backend to accept requests from different origins.
    * Essential when the frontend and backend are hosted on different domains or ports.
Benefits:
* Enables integration with frontend applications like React or Angular.
* Provides security by specifying allowed origins.

Django Channels
* Purpose: Adds support for handling WebSockets and background tasks in Django.
* Usage:
    * Facilitates real-time features like chat applications, notifications, and live updates.
    * Manages asynchronous tasks alongside traditional synchronous views.
Features:
* Channel Layers: Allows communication between different instances of the application.
* Redis Integration: Uses Redis as the message broker for handling channels.
* Backward Compatibility: Works with existing Django applications.

django-extensions
* Purpose: Provides custom extensions, management commands, and tools for Django projects.
* Usage:
    * Enhances development productivity with additional commands.
    * Offers utilities like shell_plus, which auto-imports models into the Django shell.
Features:
* Graph Models: Visualize model relationships.
* Runserver Plus: An improved development server with features like SSL support.
* Database Commands: Additional commands for database management.

drf-spectacular
* Purpose: Generates OpenAPI 3.0 schemas for your DRF API.
* Usage:
    * Automates API documentation generation.
    * Integrates with Swagger UI and ReDoc for interactive documentation.
Benefits:
* Keeps API documentation up-to-date with minimal effort.
* Improves collaboration by providing clear API specifications.

Custom Django Apps
* List of Apps:
    * users: Custom user model and authentication logic.
    * follows: Manages following relationships between users.
    * reactions: Handles user reactions like likes and dislikes.
    * stories: Implements ephemeral content similar to social media stories.
    * social: Core social networking functionalities.
    * messenger: Real-time messaging between users.
    * newsfeed: Aggregates content for user feeds.
    * pages: Allows creation and management of pages or profiles.
    * friends: Manages friend requests and relationships.
    * comments: Enables commenting on posts or content.
    * notifications: Sends in-app notifications to users.
    * albums: Manages media albums for users.
    * core: Contains shared utilities and base configurations.
Purpose:
* Modularizes the application for better maintainability.
* Encapsulates specific features and functionalities.

django-celery-beat
* Purpose: Schedules periodic tasks in Django using Celery.
* Usage:
    * Manages scheduled tasks through the Django admin interface.
    * Stores task schedules in the database.
Features:
* Dynamic Scheduling: Modify task schedules without restarting the server.
* Admin Integration: Easy management of tasks via Django admin.

Celery
* Purpose: An asynchronous task queue for executing tasks outside the HTTP request-response cycle.
* Usage:
    * Offloads long-running tasks like sending emails, generating reports, or processing images.
    * Works with brokers like Redis to manage task queues.
Benefits:
* Improves application performance by handling tasks asynchronously.
* Scalable and efficient in handling numerous tasks.

Redis
* Purpose: An in-memory data structure store used as a database, cache, and message broker.
* Usage in Project:
    * Message Broker for Celery: Facilitates communication between Celery workers and the application.
    * Channel Layer for Django Channels: Manages real-time communication channels.
    * Caching Backend: Stores frequently accessed data to reduce database load.
Benefits:
* High-speed data access.
* Supports advanced data structures.
* Scalable for handling large amounts of data.

WhiteNoise
* Purpose: Simplifies static file serving for Django applications, especially in production.
* Usage:
    * Serves static files directly from the Django application.
    * Compresses files and adds appropriate headers for caching.
Benefits:
* Eliminates the need for external services or servers for static files.
* Enhances performance by serving compressed files.

Sentry SDK
* Purpose: Provides real-time error tracking and performance monitoring.
* Usage:
    * Captures exceptions and errors in the application.
    * Sends alerts and notifications to developers.
Features:
* Detailed Stack Traces: Helps in debugging issues quickly.
* Performance Metrics: Monitors application performance and bottlenecks.
* Third-Party Integrations: Works with various tools and services for enhanced monitoring.

PostgreSQL
* Purpose: An open-source relational database system.
* Usage:
    * Stores persistent data for the application.
    * Supports advanced data types and indexing.
Benefits:
* Reliable and robust database management.
* ACID-compliant transactions.
* Scalable for large applications.

Email Backend (SMTP with Gmail)
* Purpose: Enables the application to send emails.
* Usage:
    * Uses Gmail's SMTP server for sending emails like account activation and password resets.
    * Configured with TLS for secure communication.
Features:
* Email Notifications: Keeps users informed about account activities.
* Secure Transmission: Protects data during email transmission.

Logging Configuration
* Purpose: Captures application logs for monitoring and debugging.
* Usage:
    * Logs warnings and errors to the console and a file.
    * Configured to log messages from Django and Channels.
Benefits:
* Helps in diagnosing issues.
* Keeps a record of application behavior over time.

Security Enhancements
* Purpose: Protects the application in production environments.
* Usage:
    * SECURE_SSL_REDIRECT: Forces HTTPS connections.
    * CSRF and Session Cookies: Secured with HTTPS.
    * HTTP Strict Transport Security (HSTS): Enforces secure connections over time.
    * X-Frame-Options: Prevents clickjacking attacks.
    * Content Security Policy: Mitigates cross-site scripting (XSS) attacks.
Benefits:
* Enhances overall security posture.
* Complies with best practices and standards.

Caching
* Backend: Uses Redis for caching.
* Purpose: Speeds up data retrieval and reduces database load.
* Usage:
    * Stores frequently accessed data in memory.
    * Configurable cache timeout and invalidation.
Benefits:
* Improves application performance.
* Scalable caching solution.

Error Tracking
* Tools: Sentry SDK and logging.
* Purpose: Monitors and reports errors in real-time.
* Usage:
    * Captures exceptions and sends them to Sentry.
    * Logs warnings and errors for review.
Benefits:
* Proactive error detection.
* Faster resolution of issues.

Testing Utilities
* Custom Management Commands:
    * NonInteractiveMigrationQuestioner: Automates migrations during testing.
* Purpose: Streamlines the testing process.
* Usage:
    * Automates database migrations without manual intervention.
    * Ensures tests run smoothly.
Benefits:
* Saves time during testing.
* Reduces human error.

## Technical Stack

1. Backend:

    •	Django: Serves as the primary backend framework, facilitating rapid development with built-in ORM, authentication, and admin panel.
    •	Django REST Framework (DRF): Provides robust API endpoints with features like serialization, authentication, and permission management.
    •	PostgreSQL: Relational database used for storing user data, posts, interactions, and other structured data.
    •	Django Channels: Adds support for handling WebSockets and real-time functionalities such as notifications and messaging.
    •	Celery + Redis: Celery handles asynchronous task queues (e.g., sending emails, background jobs), while Redis is used as the message broker for Celery and the channel layer for real-time communication.
    •	JWT Authentication (Simple JWT): Implements secure token-based authentication for user sessions in API interactions.
    •	Sentry SDK: Monitors real-time error tracking and performance logging to ensure system health.

2. Security & Configuration:

    •	django-environ: Manages environment variables, improving security by keeping sensitive data like keys and passwords outside the codebase.
    •	CORS Headers (django-cors-headers): Handles Cross-Origin Resource Sharing (CORS) to allow communication between frontend and backend.
    •	Security Enhancements: Includes HTTPS redirection, Content Security Policy (CSP), HSTS, and CSRF protection to secure the application in production environments.

3. Asynchronous & Task Scheduling:

    •	Celery + django-celery-beat: Celery executes background tasks, while django-celery-beat schedules periodic tasks via the Django admin panel.

4. Static Files & Caching:

    •	WhiteNoise: Simplifies static file serving for Django applications, compressing files and optimizing performance for production.
    •	Redis: Used as the caching backend to store frequently accessed data, improving performance and reducing database load.

5. API Documentation:

    •	drf-spectacular: Automatically generates OpenAPI 3.0-compliant API documentation for easy collaboration and integration with frontends.

6. Logging & Monitoring:

    •	Logging Configuration: Logs errors, warnings, and key application events, which is crucial for debugging and monitoring.
    •	Sentry SDK: Provides real-time error tracking and performance monitoring, alerting developers to issues as they occur.

7. Email & Notifications:

    •	SMTP with Gmail: Enables the backend to send transactional emails like account activation and password reset notifications using Gmail’s SMTP server.

8. Containerization & Deployment:

    •	Docker: Containerizes the entire application stack, making it easy to deploy, scale, and maintain consistency across development, staging, and production environments.

9. Testing & Development Tools:

    •	django-extensions: Adds extra management commands and tools that streamline development (e.g., shell_plus, custom database commands).
    •	Custom Management Commands: Automates database migrations and testing routines for smoother CI/CD pipelines.

10. Frontend:

     •	React: JavaScript library for building the user interface.
     •	React Router: For navigation between different views.
     •	Redux: For state management.
     •	Axios: For making API requests.

11. Mobile App:

     •	React Native: Framework for building cross-platform mobile apps.
     •	React Navigation: For handling navigation in the mobile app.
     •	Redux: For state management in the mobile app.
     •	Axios: For API interactions.

12. DevOps:

     •	GitHub Actions: For Continuous Integration/Continuous Deployment (CI/CD).
     •	Docker: Ensures consistency across different environments.
     •	Heroku: For hosting the backend API.
     •	Netlify/Vercel: For hosting the frontend application.

Installation and Setup

Clone the Repository
```sh
git clone https://github.com/your-username/SocialNetworkDjango.git
cd SocialNetworkDjango
