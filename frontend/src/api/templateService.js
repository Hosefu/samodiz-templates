const API_BASE_URL = '/api';

export const fetchTemplates = async () => {
  const response = await fetch(`${API_BASE_URL}/templates/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.statusText}`);
  }
  return await response.json();
};

export const fetchTemplateById = async (id) => {
  const response = await fetch(`${API_BASE_URL}/templates/${id}/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch template: ${response.statusText}`);
  }
  return await response.json();
};

export const createTemplate = async (templateData) => {
  const response = await fetch(`${API_BASE_URL}/templates/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
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
    headers: {
      'Content-Type': 'application/json',
    },
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
  });
  if (!response.ok) {
    throw new Error(`Failed to delete template: ${response.statusText}`);
  }
  return true;
}; 