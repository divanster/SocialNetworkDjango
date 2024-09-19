# Use an official Node.js runtime as a parent image
FROM node:20

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

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
