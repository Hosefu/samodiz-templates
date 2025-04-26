// Общие заголовки для всех API-запросов
export const getHeaders = (contentType = 'application/json') => {
  return {
    'Content-Type': contentType,
  };
}; 