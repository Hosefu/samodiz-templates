import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchTemplateById, updateTemplate } from '../../api/templateService';
import { useTemplates } from '../../context/TemplateContext';

const TemplateEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { refreshTemplates } = useTemplates();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    version: '',
    type: 'pdf'
  });

  useEffect(() => {
    const loadTemplate = async () => {
      try {
        setLoading(true);
        const data = await fetchTemplateById(id);
        setTemplate(data);
        setFormData({
          name: data.name,
          version: data.version,
          type: data.type
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    
    try {
      await updateTemplate(id, formData);
      refreshTemplates();
      alert('Template updated successfully');
    } catch (err) {
      console.error('Failed to update template:', err);
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center">Loading template...</div>;
  if (error && !template) return <div className="text-red-500">Error: {error}</div>;
  if (!template) return <div className="text-center">Template not found</div>;

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">Edit Template</h3>
        <p className="text-gray-500">Update template details and manage pages</p>
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

      <div className="bg-white shadow overflow-hidden rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Template Name
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
                <label htmlFor="version" className="block text-sm font-medium text-gray-700">
                  Version
                </label>
                <input
                  type="text"
                  name="version"
                  id="version"
                  value={formData.version}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  Type
                </label>
                <select
                  name="type"
                  id="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="pdf">PDF</option>
                  <option value="png">PNG</option>
                  <option value="svg">SVG</option>
                </select>
              </div>
            </div>
            <div className="mt-6">
              <button
                type="submit"
                disabled={saving}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-500 hover:bg-blue-600 disabled:bg-blue-400"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Pages section */}
      <div className="bg-white shadow overflow-hidden rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Pages</h3>
          <Link
            to={`/admin/templates/${id}/pages/new`}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-500 hover:bg-blue-600"
          >
            Add Page
          </Link>
        </div>
        <div className="border-t border-gray-200">
          {template.pages?.length === 0 ? (
            <div className="px-4 py-5 sm:p-6 text-center text-gray-500">
              No pages found. Add your first page!
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {template.pages?.map((page) => (
                <li key={page.name} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-md font-medium">{page.name}</h4>
                      <p className="text-sm text-gray-500">
                        {page.width}x{page.height} {page.units}, {page.fields?.length || 0} fields, {page.assets?.length || 0} assets
                      </p>
                    </div>
                    <Link
                      to={`/admin/templates/${id}/pages/${page.name}`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplateEdit; 