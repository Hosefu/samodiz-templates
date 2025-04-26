import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchTemplateById, updateTemplate } from '../../api/templateService';
import { updatePage } from '../../api/pageService';
import CodeEditor from '../../components/admin/CodeEditor';
import FileUploader from '../../components/admin/FileUploader';
import { uploadAsset, deleteAsset } from '../../api/assetService';

const PageEdit = () => {
  const { templateId, pageId } = useParams();
  const navigate = useNavigate();
  const [template, setTemplate] = useState(null);
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    width: 210,
    height: 297,
    units: 'mm',
    bleeds: 3,
    html: ''
  });
  const [fields, setFields] = useState([]);

  useEffect(() => {
    const loadTemplate = async () => {
      try {
        setLoading(true);
        const data = await fetchTemplateById(templateId);
        setTemplate(data);
        const pageData = data.pages.find(p => p.name === pageId);
        if (pageData) {
          setPage(pageData);
          setFormData({
            name: pageData.name,
            width: pageData.width,
            height: pageData.height,
            units: pageData.units,
            bleeds: pageData.bleeds,
            html: pageData.html
          });
          setFields(pageData.fields || []);
        } else {
          setError('Page not found');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [templateId, pageId]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseInt(value, 10) : value
    }));
  };

  const handleHtmlChange = (newValue) => {
    setFormData(prev => ({ ...prev, html: newValue }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    
    try {
      const pageData = {
        ...formData,
        fields,
        assets: page.assets || []
      };
      
      await updatePage(templateId, pageId, pageData);
      alert('Page updated successfully');
    } catch (err) {
      console.error('Failed to update page:', err);
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleAddField = () => {
    setFields([...fields, { name: '', label: '', required: false }]);
  };

  const handleFieldChange = (index, field) => {
    const updatedFields = [...fields];
    updatedFields[index] = field;
    setFields(updatedFields);
  };

  const handleDeleteField = (index) => {
    const updatedFields = [...fields];
    updatedFields.splice(index, 1);
    setFields(updatedFields);
  };

  const handleFileUpload = async (file) => {
    try {
      const asset = await uploadAsset(templateId, pageId, file);
      setPage(prev => ({
        ...prev,
        assets: [...(prev.assets || []), asset]
      }));
    } catch (err) {
      console.error('Failed to upload file:', err);
      alert('Failed to upload file. Please try again.');
    }
  };

  const handleDeleteAsset = async (assetId) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        await deleteAsset(templateId, pageId, assetId);
        setPage(prev => ({
          ...prev,
          assets: prev.assets.filter(a => a.id !== assetId)
        }));
      } catch (err) {
        console.error('Failed to delete asset:', err);
        alert('Failed to delete asset. Please try again.');
      }
    }
  };

  if (loading) return <div className="text-center">Loading page...</div>;
  if (error && !page) return <div className="text-red-500">Error: {error}</div>;
  if (!page) return <div className="text-center">Page not found</div>;

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">Edit Page</h3>
        <p className="text-gray-500">Update page details and manage assets</p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div>
              <p className="text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Page Details Section */}
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h4 className="text-lg font-medium mb-4">Page Details</h4>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Page Name
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label htmlFor="width" className="block text-sm font-medium text-gray-700">
                  Width
                </label>
                <input
                  type="number"
                  name="width"
                  id="width"
                  value={formData.width}
                  onChange={handleChange}
                  required
                  min="1"
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label htmlFor="height" className="block text-sm font-medium text-gray-700">
                  Height
                </label>
                <input
                  type="number"
                  name="height"
                  id="height"
                  value={formData.height}
                  onChange={handleChange}
                  required
                  min="1"
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label htmlFor="units" className="block text-sm font-medium text-gray-700">
                  Units
                </label>
                <select
                  name="units"
                  id="units"
                  value={formData.units}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="mm">Millimeters (mm)</option>
                  <option value="px">Pixels (px)</option>
                </select>
              </div>
              <div>
                <label htmlFor="bleeds" className="block text-sm font-medium text-gray-700">
                  Bleeds
                </label>
                <input
                  type="number"
                  name="bleeds"
                  id="bleeds"
                  value={formData.bleeds}
                  onChange={handleChange}
                  min="0"
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>
        </div>

        {/* HTML Editor Section */}
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h4 className="text-lg font-medium mb-4">HTML Template</h4>
            <CodeEditor
              value={formData.html}
              onChange={handleHtmlChange}
              language="html"
              height="400px"
            />
          </div>
        </div>

        {/* Fields Section */}
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium">Template Fields</h4>
              <button
                type="button"
                onClick={handleAddField}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Add Field
              </button>
            </div>
            <div className="space-y-4">
              {fields.map((field, index) => (
                <div key={index} className="grid grid-cols-1 gap-4 sm:grid-cols-3 items-end">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Field Name
                    </label>
                    <input
                      type="text"
                      value={field.name}
                      onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })}
                      className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      placeholder="field_name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Label
                    </label>
                    <input
                      type="text"
                      value={field.label}
                      onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })}
                      className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      placeholder="Field Label"
                    />
                  </div>
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={field.required}
                        onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">Required</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => handleDeleteField(index)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Assets Section */}
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h4 className="text-lg font-medium mb-4">Assets</h4>
            <FileUploader onFileUpload={handleFileUpload} templateId={templateId} pageId={pageId} />
            {page.assets?.length > 0 && (
              <div className="mt-6">
                <h5 className="text-sm font-medium text-gray-700 mb-3">Uploaded Assets</h5>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {page.assets.map((asset) => {
                    const fileName = asset.file ? asset.file.split('/').pop() : 'Unknown file';
                    const isImage = /\.(jpg|jpeg|png|gif|svg)$/i.test(asset.file || '');
                    
                    return (
                      <div key={asset.id} className="relative group">
                        <div className="aspect-w-1 aspect-h-1 rounded-lg bg-gray-100 overflow-hidden">
                          {isImage ? (
                            <img
                              src={asset.file}
                              alt={fileName}
                              className="object-cover"
                            />
                          ) : (
                            <div className="flex items-center justify-center h-full">
                              <span className="text-gray-500">{fileName}</span>
                            </div>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => handleDeleteAsset(asset.id)}
                          className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate(`/admin/templates/${templateId}`)}
            className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PageEdit; 