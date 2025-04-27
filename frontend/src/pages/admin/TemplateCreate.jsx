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

const TPL_CREATE_TITLE = "Создание нового шаблона";
const TPL_CREATE_DESCRIPTION = "Введите основную информацию для вашего шаблона.";
const TPL_CREATE_NAME_LABEL = "Название шаблона";
const TPL_CREATE_NAME_PLACEHOLDER = "Например, Счет-фактура";
const TPL_CREATE_VERSION_LABEL = "Версия";
const TPL_CREATE_VERSION_PLACEHOLDER = "1.0";
const TPL_CREATE_TYPE_LABEL = "Тип выходного файла";
const TPL_CREATE_ERROR = (msg) => `Не удалось создать шаблон: ${msg}`;
const TPL_CREATE_SUBMIT_BUTTON = "Создать и перейти к страницам";
const TPL_CREATE_SUBMITTING_BUTTON = "Создание...";
const TPL_CREATE_CANCEL_BUTTON = "Отмена";

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
  const [fields, setFields] = useState([
    // Убираем начальные поля или используем константы
    // { name: 'title', label: text.PAGE_CREATE_FIELD_DEFAULT_TITLE, required: true },
    // { name: 'name', label: text.PAGE_CREATE_FIELD_DEFAULT_NAME, required: true }
  ]);

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
      setError(TPL_CREATE_ERROR(err.message || text.UNKNOWN_ERROR_MSG));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">Create New Template</h3>
        <p className="text-gray-500">Enter the basic information for your template</p>
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
                  Template Name
                </label>
                <Input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  placeholder="Invoice Template"
                  error={error && !formData.name ? text.REQUIRED_ERROR_MSG(TPL_CREATE_NAME_LABEL) : null}
                />
              </div>
              <div>
                <label htmlFor="version" className="block text-sm font-medium text-gray-700">
                  Version
                </label>
                <Input
                  type="text"
                  name="version"
                  id="version"
                  value={formData.version}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  placeholder="1.0"
                  error={error && !formData.version ? text.REQUIRED_ERROR_MSG(TPL_CREATE_VERSION_LABEL) : null}
                />
              </div>
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  Type
                </label>
                <Select
                  name="type"
                  id="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                  className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  error={error && !formData.type ? text.REQUIRED_ERROR_MSG(TPL_CREATE_TYPE_LABEL) : null}
                >
                  <option value="pdf">PDF</option>
                  <option value="png">PNG</option>
                  <option value="svg">SVG</option>
                </Select>
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <Button
                type="button"
                onClick={() => navigate('/admin/templates')}
                className="mr-3 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                {TPL_CREATE_CANCEL_BUTTON}
              </Button>
              <Button
                type="submit"
                disabled={loading}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
              >
                {loading ? TPL_CREATE_SUBMITTING_BUTTON : TPL_CREATE_SUBMIT_BUTTON}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TemplateCreate; 