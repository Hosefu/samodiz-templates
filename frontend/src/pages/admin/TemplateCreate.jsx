import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createTemplate } from '../../api/templateService';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import Select from '../../components/ui/Select';
import { ChevronLeft, Save } from 'lucide-react';

const TemplateCreate = () => {
  const navigate = useNavigate();
  const { refreshTemplates } = useTemplates();
  const [formData, setFormData] = useState({
    name: '',
    version: '1.0',
    type: 'pdf'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const newTemplate = await createTemplate(formData);
      refreshTemplates();
      navigate(`/admin/templates/${newTemplate.id}`);
    } catch (err) {
      console.error('Failed to create template:', err);
      setError(text.TEMPLATE_CREATE_ERROR(err.message || text.UNKNOWN_ERROR_MSG));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">{text.TEMPLATE_CREATE_TITLE}</h3>
        <p className="text-gray-500">{text.TEMPLATE_CREATE_DESCRIPTION}</p>
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

      <div className="bg-white shadow overflow-hidden rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  {text.TEMPLATE_CREATE_NAME_LABEL}
                </label>
                <Input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  placeholder={text.TEMPLATE_CREATE_NAME_PLACEHOLDER}
                  error={error && !formData.name ? text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_NAME_LABEL) : null}
                />
              </div>
              <div>
                <label htmlFor="version" className="block text-sm font-medium text-gray-700">
                  {text.TEMPLATE_CREATE_VERSION_LABEL}
                </label>
                <Input
                  type="text"
                  name="version"
                  id="version"
                  value={formData.version}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  placeholder={text.TEMPLATE_CREATE_VERSION_PLACEHOLDER}
                  error={error && !formData.version ? text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_VERSION_LABEL) : null}
                />
              </div>
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  {text.TEMPLATE_CREATE_TYPE_LABEL}
                </label>
                <Select
                  name="type"
                  id="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  error={error && !formData.type ? text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_TYPE_LABEL) : null}
                >
                  <option value="">{text.TEMPLATE_CREATE_SELECT_TYPE}</option>
                  <option value="pdf">PDF</option>
                  <option value="docx">DOCX</option>
                  <option value="xlsx">XLSX</option>
                  <option value="html">HTML</option>
                </Select>
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <Button
                type="button"
                onClick={() => navigate('/admin/templates')}
                className="mr-3 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                {text.CANCEL_BUTTON}
              </Button>
              <Button
                type="submit"
                disabled={loading}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
              >
                {loading ? text.TEMPLATE_CREATE_SUBMITTING_BUTTON : text.TEMPLATE_CREATE_SUBMIT_BUTTON}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TemplateCreate; 