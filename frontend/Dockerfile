# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build the app
RUN npm run build

# Final stage - the build output will be used by Nginx
# The actual serving is done by the Nginx container defined in the main Dockerfile

FROM node:18-alpine

WORKDIR /app

# Копируем файлы package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/node_modules/.vite

# Устанавливаем переменные окружения
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost/api
ENV VITE_STORAGE_URL=http://localhost/storage
ENV VITE_PDF_URL=http://localhost/pdf
ENV VITE_PNG_URL=http://localhost/png

# Открываем порт
EXPOSE 5173

# Запускаем dev-сервер
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]