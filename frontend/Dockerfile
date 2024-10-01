# frontend/Dockerfile

# Stage 1: Build the React application
FROM node:20 AS build

# Declare build arguments
ARG CHOKIDAR_USEPOLLING
ARG NODE_OPTIONS
ARG REACT_APP_API_URL

# Set environment variables from build arguments
ENV CHOKIDAR_USEPOLLING=${CHOKIDAR_USEPOLLING}
ENV NODE_OPTIONS=${NODE_OPTIONS}
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the React application using Nginx
FROM nginx:alpine

# Copy the build output to Nginx's HTML directory
COPY --from=build /app/build /usr/share/nginx/html

# Optional: Remove the default Nginx configuration and use a custom one
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
