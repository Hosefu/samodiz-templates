import { getHeaders } from '../utils/apiConfig';
import { getAuthHeaders } from './templateService';

const API_BASE_URL = '/api';

export const uploadAsset = async (templateId, pageId, file) => {
  const formData = new FormData();
  formData.append('file', file);

  // Получаем токен из localStorage
  const tokensStr = localStorage.getItem('tokens');
  
  // Для multipart/form-data заголовок Content-Type не указываем,
  // он будет установлен автоматически с правильной boundary
  let headers = {};
  
  // Если есть токен, добавляем его в заголовки запроса
  if (tokensStr) {
    const tokens = JSON.parse(tokensStr);
    headers['Authorization'] = `Bearer ${tokens.access}`;
  }

  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/assets/`, {
    method: 'POST',
    headers: headers,
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`Failed to upload asset: ${response.statusText}`);
  }
  return await response.json();
};

export const deleteAsset = async (templateId, pageId, assetId) => {
  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/assets/${assetId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete asset: ${response.statusText}`);
  }
  return true;
}; 