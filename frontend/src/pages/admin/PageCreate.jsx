import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createPage } from '../../api/pageService';
import CodeEditor from '../../components/admin/CodeEditor';

const PageCreate = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    width: 210,
    height: 297,
    units: 'mm',
    bleeds: 3,
    html: '<!DOCTYPE html>\n<html>\n<head>\n  <title>Page Template</title>\n  <style>\n    body {\n      font-family: Arial, sans-serif;\n      margin: 0;\n      padding: 20px;\n    }\n    h1 { color: #333; }\n  </style>\n</head>\n<body>\n  <h1>{{title}}</h1>\n  <p>Hello, {{name}}!</p>\n</body>\n</html>'
  });
  const [fields, setFields] = useState([
    { name: 'title', label: 'Title', required: true },
    { name: 'name', label: 'Name', required: true }
  ]);

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
    setLoading(true);
    setError(null);
    
    try {
      const pageData = {
        ...formData,
        fields,
        assets: []
      };
      
      const newPage = await createPage(templateId, pageData);
      navigate(`/admin/templates/${templateId}/pages/${newPage.name}`);
    } catch (err) {
      console.error('Failed to create page:', err);
      setError(err.message);
    } finally {
      setLoading(false);
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

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">Create New Page</h3>
        <p className="text-gray-500">Add a page to template ID: {templateId}</p>
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
            disabled={loading}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
          >
            {loading ? 'Creating...' : 'Create Page'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PageCreate; 