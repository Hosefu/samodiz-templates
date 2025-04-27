import { getAuthHeaders } from './templateService';

const API_BASE_URL = '/api';

export const createPage = async (templateId, pageData) => {
  try {
    console.log('Creating page with data:', pageData);
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(pageData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      console.error('Failed to create page:', response.status, response.statusText, errorData);
      throw new Error(errorData?.detail || `Failed to create page: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Page created successfully:', data);
    return data;
  } catch (error) {
    console.error('Error in createPage:', error);
    throw error;
  }
};

export const updatePage = async (templateId, pageId, pageData) => {
  try {
    console.log('Updating page with data:', pageData);
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(pageData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      console.error('Failed to update page:', response.status, response.statusText, errorData);
      throw new Error(errorData?.detail || `Failed to update page: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Page updated successfully:', data);
    return data;
  } catch (error) {
    console.error('Error in updatePage:', error);
    throw error;
  }
};

export const deletePage = async (templateId, pageId) => {
  try {
    console.log('Deleting page:', pageId);
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      console.error('Failed to delete page:', response.status, response.statusText, errorData);
      throw new Error(errorData?.detail || `Failed to delete page: ${response.statusText}`);
    }
    
    console.log('Page deleted successfully');
    return true;
  } catch (error) {
    console.error('Error in deletePage:', error);
    throw error;
  }
}; 