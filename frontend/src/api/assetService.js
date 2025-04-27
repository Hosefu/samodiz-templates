import { getAuthHeaders } from './templateService';

// Константы для валидации файлов
const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/svg+xml',
  'application/pdf'
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

// Функция валидации файла
const validateFile = (file) => {
  // Проверка размера
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`Размер файла превышает максимально допустимый (${MAX_FILE_SIZE/1024/1024}MB)`);
  }

  // Проверка типа файла
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    throw new Error(`Тип файла ${file.type} не поддерживается. Поддерживаемые типы: ${ALLOWED_MIME_TYPES.join(', ')}`);
  }

  return true;
};

export const uploadAsset = async (templateId, pageId, file) => {
  try {
    // Валидация файла перед загрузкой
    validateFile(file);

    const formData = new FormData();
    formData.append('file', file);

    // Получаем токен из Redux store или localStorage
    const tokensStr = localStorage.getItem('tokens');
    
    // Для multipart/form-data заголовок Content-Type не указываем,
    // он будет установлен автоматически с правильной boundary
    let headers = {};
    
    // Если есть токен, добавляем его в заголовки запроса
    if (tokensStr) {
      const tokens = JSON.parse(tokensStr);
      headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    // Добавляем просмотр отправляемого FormData для отладки
    console.log('Uploading file:', file.name, file.type, file.size);
    
    const response = await fetch(`/api/templates/${templateId}/pages/${pageId}/assets/`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    // Полная диагностика ответа
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries([...response.headers.entries()]),
        body: errorText
      });
      
      try {
        // Пытаемся разобрать как JSON, если возможно
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.detail || `Failed to upload asset: ${response.statusText}`);
      } catch (e) {
        throw new Error(`Failed to upload asset: ${response.statusText}, ${errorText.substring(0, 100)}`);
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
    const tokensStr = localStorage.getItem('tokens');
    let headers = {
      'Content-Type': 'application/json'
    };
    
    if (tokensStr) {
      const tokens = JSON.parse(tokensStr);
      headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    const response = await fetch(`/api/templates/${templateId}/pages/${pageId}/assets/${assetId}/`, {
      method: 'DELETE',
      headers
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete asset: ${response.statusText}, ${errorText}`);
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