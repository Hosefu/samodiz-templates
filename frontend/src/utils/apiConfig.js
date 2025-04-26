// Используем правильное значение API-ключа из настроек Django
export const API_KEY = 'development-pdf-api-key';

// Общие заголовки для всех API-запросов
export const getHeaders = (contentType = 'application/json') => {
  return {
    'Content-Type': contentType,
    'X-API-Key': API_KEY,
  };
}; 