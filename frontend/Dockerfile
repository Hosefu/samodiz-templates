FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build static files
RUN npm run build

# Production image
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Default nginx config for React apps
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]