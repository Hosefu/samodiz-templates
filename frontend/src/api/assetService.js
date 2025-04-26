import { getHeaders } from '../utils/apiConfig';

const API_BASE_URL = '/api';

export const uploadAsset = async (templateId, pageId, file) => {
  const formData = new FormData();
  formData.append('file', file);

  // Для multipart/form-data заголовок Content-Type не указываем,
  // он будет установлен автоматически с правильной boundary
  const headers = {
    'X-API-Key': getHeaders()['X-API-Key']
  };

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
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete asset: ${response.statusText}`);
  }
  return true;
}; 