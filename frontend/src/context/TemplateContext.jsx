import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchTemplates } from '../api/templateService';

const TemplateContext = createContext();

export const TemplateProvider = ({ children }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTemplates();
      setTemplates(data);
    } catch (err) {
      console.error('Error loading templates:', err);
      setError(err.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const selectTemplate = (template) => {
    setSelectedTemplate(template);
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  return (
    <TemplateContext.Provider
      value={{
        templates,
        loading,
        error,
        refreshTemplates: loadTemplates,
        setTemplates,
        selectedTemplate,
        selectTemplate
      }}
    >
      {children}
    </TemplateContext.Provider>
  );
};

export const useTemplates = () => {
  const context = useContext(TemplateContext);
  if (context === undefined) {
    throw new Error('useTemplates must be used within a TemplateProvider');
  }
  return context;
}; 