import { getAuthHeaders } from './templateService';
import * as text from '../constants/ux-writing';

// Constants for file validation
const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/svg+xml',
  'application/pdf',
  'font/ttf',
  'font/otf',
  'application/font-sfnt' // For some TTF/OTF files
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

// File validation function
const validateFile = (file) => {
  if (!file) {
    throw new Error('Файл не выбран');
  }
  
  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`Размер файла превышает максимально допустимый (${MAX_FILE_SIZE/1024/1024}MB)`);
  }

  // Check file type - be more lenient for font files where MIME type might be wrong
  const isFontFile = file.name && (file.name.endsWith('.ttf') || file.name.endsWith('.otf'));
  
  if (!isFontFile && !ALLOWED_MIME_TYPES.includes(file.type)) {
    throw new Error(`Тип файла ${file.type || 'не определен'} не поддерживается. Поддерживаемые типы: JPG, PNG, GIF, SVG, PDF, TTF, OTF`);
  }

  return true;
};

export const uploadAsset = async (templateId, pageId, file) => {
  try {
    if (!file) {
      throw new Error('Файл не выбран');
    }
    
    // Validate file before upload
    validateFile(file);

    const formData = new FormData();
    formData.append('file', file);

    // Get headers with authentication token
    const headers = getAuthHeaders();
    // Don't set Content-Type for FormData, browser will set it with boundary
    delete headers['Content-Type'];

    console.log('Uploading file to server:', file.name, file.type, file.size);
    
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
        throw new Error(errorData.error || errorData.detail || `Ошибка загрузки ассета: ${response.statusText}`);
      } catch (e) {
        if (e instanceof SyntaxError) {
          // If JSON parsing failed, use the original error text
          throw new Error(`Ошибка загрузки ассета: ${response.statusText} - ${errorText}`);
        }
        throw e;
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
    const response = await fetch(`/api/templates/${templateId}/pages/${pageId}/assets/${assetId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Delete asset error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || errorData.detail || `Ошибка удаления ассета: ${response.statusText}`);
      } catch (e) {
        if (e instanceof SyntaxError) {
          throw new Error(`Ошибка удаления ассета: ${response.statusText}`);
        }
        throw e;
      }
    }
    
    return true;
  } catch (error) {
    console.error('Delete asset failed:', error);
    throw error;
  }
};

export const getAssetUrl = (templateId, pageId, assetId) => {
  return `/api/templates/${templateId}/pages/${pageId}/assets/${assetId}/`;
}; 