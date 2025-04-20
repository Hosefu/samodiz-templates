FROM node:20-alpine as build

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Используем прямой путь к ES модульному скрипту Vite CLI
RUN node node_modules/vite/dist/node/cli.js build

# Production image (Nginx to serve static files)
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Default Nginx config for single-page applications (React)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]