# Stage 1: frontend build
FROM node:18-alpine as frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

# Stage 2: nginx
FROM nginx:alpine
COPY --from=frontend-builder /app/build /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Создаем директории для статических файлов
RUN mkdir -p /usr/share/nginx/html/static /usr/share/nginx/html/media /usr/share/nginx/html/pdfs && \
    chmod -R 777 /usr/share/nginx/html/static /usr/share/nginx/html/media /usr/share/nginx/html/pdfs