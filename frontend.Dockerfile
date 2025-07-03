# Frontend Dockerfile for Vue.js application
FROM node:18-alpine as build-stage

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ .

# Copy production environment file
COPY frontend/.env.production .env.production

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Copy built application
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]