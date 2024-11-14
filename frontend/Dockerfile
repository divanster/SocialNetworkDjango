# Use the official Node.js image as the base
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 (default port for React development server)
EXPOSE 3000

# Set environment variable to fix OpenSSL issue
ENV NODE_OPTIONS="--openssl-legacy-provider"

# Start the React development server
CMD ["npm", "start"]
