import { getAuthHeaders } from './templateService';
import * as text from '../constants/ux-writing';

// Constants for file validation
const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/svg+xml',
  'application/pdf'
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

// File validation function
const validateFile = (file) => {
  if (!file) {
    throw new Error('No file provided');
  }
  
  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`File size exceeds the maximum allowed size (${MAX_FILE_SIZE/1024/1024}MB)`);
  }

  // Check file type
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    throw new Error(`File type ${file.type} is not supported. Supported types: ${ALLOWED_MIME_TYPES.join(', ')}`);
  }

  return true;
};

export const uploadAsset = async (templateId, pageId, file) => {
  try {
    if (!file) {
      throw new Error('No file provided');
    }
    
    // Validate file before upload
    validateFile(file);

    const formData = new FormData();
    formData.append('file', file);

    // Get headers with authentication token
    const headers = getAuthHeaders();
    // Don't set Content-Type for FormData, browser will set it with boundary
    delete headers['Content-Type'];

    console.log('Uploading file:', file.name, file.type, file.size);
    
    const response = await fetch(`/api/templates/${templateId}/pages/${pageId}/assets/`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload error response:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      
      try {
        // Try to parse as JSON if possible
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.detail || `Failed to upload asset: ${response.statusText}`);
      } catch (e) {
        throw new Error(`Failed to upload asset: ${response.statusText}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('Asset upload failed:', error);
    throw error;
  }
};

export const deleteAsset = async (templateId, pageId, assetId) => {
  try {
    const headers = getAuthHeaders();

    const response = await fetch(`/api/templates/${templateId}/pages/${pageId}/assets/${assetId}/`, {
      method: 'DELETE',
      headers
    });

    if (!response.ok) {
      throw new Error(`Failed to delete asset: ${response.statusText}`);
    }

    return true;
  } catch (error) {
    console.error('Asset deletion failed:', error);
    throw error;
  }
};

export const getAssetUrl = (templateId, pageId, assetId) => {
  return `/api/templates/${templateId}/pages/${pageId}/assets/${assetId}/`;
}; 