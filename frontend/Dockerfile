# Stage 1: Build the React application
FROM node:20 AS build

WORKDIR /app

# Set environment variable to fix OpenSSL issue
ENV NODE_OPTIONS="--openssl-legacy-provider"

# Copy package.json and package-lock.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React application
RUN npm run build

# Stage 2: Serve the React application using Nginx
FROM nginx:alpine

# Copy build files from Stage 1 to the Nginx HTML folder
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
