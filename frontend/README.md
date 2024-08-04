# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

# ReactRouterBootstrap Sharing Application

This is a recipe sharing application with a Django backend and React frontend, featuring user authentication, real-time messaging, and notifications.

## Features

- User authentication (registration, login, logout)
- ReactRouterBootstrap creation, editing, and deletion
- Real-time messaging between users
- Notifications for various events (e.g., new messages, new comments on recipes)
- Image upload for recipes and user profiles

## Technology Stack

- **Backend**: Django, Django REST Framework, Channels (for WebSockets), PostgreSQL
- **Frontend**: React, Redux, Bootstrap
- **CI/CD**: GitHub Actions

## Installation

### Backend

1. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   pip install -r requirements.dev.txt
   ```

3. Apply the migrations:
   ```sh
   python manage.py migrate
   ```

4. Run the development server:
   ```sh
   python manage.py runserver
   ```

### Frontend

1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```

2. Install the dependencies:
   ```sh
   npm install
   ```

3. Start the development server:
   ```sh
   npm start
   ```

## Running Tests

### Backend
```sh
python manage.py test
