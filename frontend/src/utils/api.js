const API_BASE_URL = '/api';

export const fetchTemplates = async () => {
  const response = await fetch(`${API_BASE_URL}/templates/`);
  if (!response.ok) {
    throw new Error('Не удалось загрузить шаблоны');
  }
  return await response.json();
};

export const generateDocument = async (templateId, data) => {
  const response = await fetch(`${API_BASE_URL}/render/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      template_id: templateId,
      data,
    }),
  });

  if (!response.ok) {
    throw new Error('Не удалось сгенерировать документ');
  }

  return await response.json();
}; 