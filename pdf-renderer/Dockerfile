FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app
COPY --from=build /app ./

# Создаем каталог для временного хранения сгенерированных файлов
RUN mkdir -p /app/wwwroot && \
    chmod -R 777 /app/wwwroot

# Открываем порт 8081 для API
EXPOSE 8081

# Запускаем приложение
ENTRYPOINT ["dotnet", "pdf-renderer.dll"]