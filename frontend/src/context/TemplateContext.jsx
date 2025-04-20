import React, { createContext, useContext, useState } from 'react';
import { useTemplates } from '../hooks';

const TemplateContext = createContext();

export const TemplateProvider = ({ children }) => {
  const { templates, isLoading, error, fetchTemplates } = useTemplates();
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const selectTemplate = (template) => {
    setSelectedTemplate(template);
  };

  const clearSelectedTemplate = () => {
    setSelectedTemplate(null);
  };

  return (
    <TemplateContext.Provider 
      value={{ 
        templates, 
        isLoading, 
        error, 
        selectedTemplate, 
        selectTemplate, 
        clearSelectedTemplate,
        refreshTemplates: fetchTemplates
      }}
    >
      {children}
    </TemplateContext.Provider>
  );
};

export const useTemplateContext = () => {
  const context = useContext(TemplateContext);
  if (!context) {
    throw new Error('useTemplateContext must be used within a TemplateProvider');
  }
  return context;
}; 