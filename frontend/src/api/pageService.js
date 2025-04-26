import { getHeaders } from '../utils/apiConfig';
import { getAuthHeaders } from './templateService';

const API_BASE_URL = '/api';

export const createPage = async (templateId, pageData) => {
  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(pageData),
  });
  if (!response.ok) {
    throw new Error(`Failed to create page: ${response.statusText}`);
  }
  return await response.json();
};

export const updatePage = async (templateId, pageId, pageData) => {
  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(pageData),
  });
  if (!response.ok) {
    throw new Error(`Failed to update page: ${response.statusText}`);
  }
  return await response.json();
};

export const deletePage = async (templateId, pageId) => {
  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete page: ${response.statusText}`);
  }
  return true;
}; 