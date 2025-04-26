import { getHeaders } from '../utils/apiConfig';

const API_BASE_URL = '/api';

// Вспомогательная функция для получения заголовков с токеном авторизации
export const getAuthHeaders = () => {
  // Получаем токен из localStorage
  const tokensStr = localStorage.getItem('tokens');
  let headers = getHeaders();
  
  // Если есть токен, добавляем его в заголовки запроса
  if (tokensStr) {
    const tokens = JSON.parse(tokensStr);
    headers = {
      ...headers,
      'Authorization': `Bearer ${tokens.access}`
    };
  }
  
  return headers;
};

export const fetchTemplates = async () => {
  const response = await fetch(`${API_BASE_URL}/templates/`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.statusText}`);
  }
  return await response.json();
};

export const fetchTemplateById = async (id) => {
  const response = await fetch(`${API_BASE_URL}/templates/${id}/`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch template: ${response.statusText}`);
  }
  return await response.json();
};

export const createTemplate = async (templateData) => {
  const response = await fetch(`${API_BASE_URL}/templates/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(templateData),
  });
  if (!response.ok) {
    throw new Error(`Failed to create template: ${response.statusText}`);
  }
  return await response.json();
};

export const updateTemplate = async (id, templateData) => {
  const response = await fetch(`${API_BASE_URL}/templates/${id}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(templateData),
  });
  if (!response.ok) {
    throw new Error(`Failed to update template: ${response.statusText}`);
  }
  return await response.json();
};

export const deleteTemplate = async (id) => {
  const response = await fetch(`${API_BASE_URL}/templates/${id}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete template: ${response.statusText}`);
  }
  return true;
}; 