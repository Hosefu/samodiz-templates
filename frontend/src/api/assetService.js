const API_BASE_URL = '/api';

export const uploadAsset = async (templateId, pageId, file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/templates/${templateId}/pages/${pageId}/assets/`, {
    method: 'POST',
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
  });
  if (!response.ok) {
    throw new Error(`Failed to delete asset: ${response.statusText}`);
  }
  return true;
}; 