import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchTemplateById } from '../../api/templateService';
import { updatePage } from '../../api/pageService';
import * as text from '../../constants/ux-writing';
import PageForm from '../../components/admin/PageForm';
import { toast } from 'react-hot-toast';

const PageEdit = () => {
  const { templateId, pageId } = useParams();
  const navigate = useNavigate();
  const [templateName, setTemplateName] = useState('');
  const [pageData, setPageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Load page data
  const loadPageData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const templateData = await fetchTemplateById(templateId);
      setTemplateName(templateData.name);
      
      const page = templateData.pages.find(p => p.name === pageId);
      if (page) {
        setPageData(page);
      } else {
        setError('Страница не найдена в этом шаблоне.');
      }
    } catch (err) {
      console.error('Error loading page data:', err);
      setError(`Ошибка загрузки страницы: ${err.message || text.UNKNOWN_ERROR_MSG}`);
      toast.error(`Ошибка загрузки страницы: ${err.message || text.UNKNOWN_ERROR_MSG}`);
    } finally {
      setLoading(false);
    }
  }, [templateId, pageId]);

  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  // Handle form submission
  const handleSubmit = async (formData) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      await updatePage(templateId, pageId, formData);
      toast.success('Страница успешно обновлена');
      navigate(`/admin/templates/${templateId}`);
    } catch (err) {
      console.error('Failed to update page:', err);
      const errorMsg = err.response?.data?.detail || err.message || text.UNKNOWN_ERROR_MSG;
      setError(`Ошибка обновления страницы: ${errorMsg}`);
      toast.error(`Ошибка обновления страницы: ${errorMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка страницы...</p>
        </div>
      </div>
    );
  }

  if (error && !pageData) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 my-4 rounded-md">
        <h3 className="font-semibold">Ошибка</h3>
        <p>{error}</p>
        <button 
          onClick={() => navigate(`/admin/templates/${templateId}`)}
          className="mt-2 text-blue-600 hover:underline"
        >
          Вернуться к шаблону
        </button>
      </div>
    );
  }

  return (
    <PageForm
      mode="edit"
      templateId={templateId}
      templateName={templateName}
      pageId={pageId}
      initialData={pageData}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      error={error}
    />
  );
};

export default PageEdit;