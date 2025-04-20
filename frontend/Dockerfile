FROM node:20-alpine as build

WORKDIR /app

# Сначала копируем только файлы пакетов для кэширования слоев
COPY package*.json ./

# Используем явную установку vite и установку зависимостей
RUN npm install -g vite
RUN npm install

# Копируем исходный код
COPY . .

# Используем глобальный vite для сборки
RUN vite build

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