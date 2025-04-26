FROM node:20-alpine as build

WORKDIR /app

# Копируем только файлы для установки пакетов
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы проекта
COPY . .

# Собираем проект для production
RUN npm run build

# Второй этап - легкий nginx контейнер с собранным приложением
FROM nginx:alpine

# Копируем собранный проект
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 