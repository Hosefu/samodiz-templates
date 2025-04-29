import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createPage } from '../../api/pageService';
import { fetchTemplateById } from '../../api/templateService';
import * as text from '../../constants/ux-writing';
import PageForm from '../../components/admin/PageForm';
import { toast } from 'react-hot-toast';

const PageCreate = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [templateName, setTemplateName] = useState('');

  // Fetch template name for breadcrumbs
  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const template = await fetchTemplateById(templateId);
        setTemplateName(template.name);
      } catch (err) {
        console.error('Error fetching template:', err);
      }
    };

    fetchTemplate();
  }, [templateId]);

  const handleSubmit = async (pageData) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      console.log('Sending page data:', pageData);
      const newPage = await createPage(templateId, pageData);
      console.log('Page created successfully:', newPage);
      
      toast.success(`Страница "${newPage.name}" успешно создана!`);
      navigate(`/admin/templates/${templateId}`); 
    } catch (err) {
      console.error('Failed to create page:', err);
      const errorMsg = err.response?.data?.detail || err.message || text.UNKNOWN_ERROR_MSG;
      setError(`Не удалось создать страницу: ${errorMsg}`);
      toast.error(`Не удалось создать страницу: ${errorMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageForm
      mode="create"
      templateId={templateId}
      templateName={templateName}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      error={error}
    />
  );
};

export default PageCreate; 