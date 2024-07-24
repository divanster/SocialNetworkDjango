# SocialNetworkDjango

## Overview

SocialNetworkDjango is a comprehensive web and mobile application designed as a social networking platform. The project consists of a Django backend that serves a RESTful API and a React frontend that provides an intuitive user interface. The application supports user authentication, post creation, rating, commenting, real-time messaging, and much more.

## Features

1. **User Authentication:**
   - User registration and login.
   - Password reset functionality.
   - JWT-based authentication for secure API access.

2. **Post Management:**
   - Users can create, read, update, and delete posts.
   - Posts can include content, tags, and images.
   - Default images are provided for posts without images.

3. **Social Features:**
   - Users can follow other users to see their posts.
   - React (like, love, etc.) and comment on posts.
   - Notifications for various user interactions.

4. **Real-Time Messaging:**
   - Users can send and receive real-time messages.
   - WebSocket integration for instant messaging.
   - Notifications for new messages.

5. **Search and Filter:**
   - Search for posts by title or tags.
   - Filter posts based on user preferences.

6. **Mobile App:**
   - A mobile app version is available, providing the same functionalities as the web version.
   - The mobile app is built using React Native, ensuring a seamless experience across both iOS and Android platforms.

## Technical Stack

1. **Backend:**
   - **Django:** Serves as the primary backend framework.
   - **Django REST Framework (DRF):** Provides robust API endpoints.
   - **PostgreSQL:** Database for storing user data, posts, and interactions.
   - **Channels:** For real-time functionalities like notifications and messaging.
   - **JWT Authentication:** For secure user sessions.
   - **Docker:** Containerization for easy deployment and scaling.

2. **Frontend:**
   - **React:** JavaScript library for building the user interface.
   - **React Router:** For navigation between different views.
   - **Redux:** For state management.
   - **Axios:** For making API requests.

3. **Mobile App:**
   - **React Native:** Framework for building cross-platform mobile apps.
   - **React Navigation:** For handling navigation in the mobile app.
   - **Redux:** For state management in the mobile app.
   - **Axios:** For API interactions.

4. **DevOps:**
   - **GitHub Actions:** For Continuous Integration/Continuous Deployment (CI/CD).
   - **Docker:** Ensures consistency across different environments.
   - **Heroku:** For hosting the backend API.
   - **Netlify/Vercel:** For hosting the frontend application.

## Installation and Setup

### Clone the Repository
```sh
git clone https://github.com/your-username/SocialNetworkDjango.git
cd SocialNetworkDjango
