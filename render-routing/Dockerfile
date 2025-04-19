FROM golang:1.21-alpine AS build

WORKDIR /app

# Установка необходимых зависимостей
RUN apk --no-cache add ca-certificates git

# Копирование файлов go.mod и go.sum и загрузка зависимостей
COPY go.mod go.sum ./
RUN go mod download

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o render-routing ./cmd/server

# Создание минимального образа
FROM alpine:3.18

WORKDIR /app

# Установка сертификатов и tzdata
RUN apk --no-cache add ca-certificates tzdata

# Копирование бинарного файла из образа сборки
COPY --from=build /app/render-routing .

# Определение порта, который будет прослушивать приложение
EXPOSE 8080

# Команда для запуска приложения
CMD ["./render-routing"]