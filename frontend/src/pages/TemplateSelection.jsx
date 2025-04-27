import React from 'react';
import { Card } from '../components/ui';
import { TemplateList } from '../components/templates';
import { useTemplateContext } from '../context/TemplateContext';
import * as text from '../../constants/ux-writing';

const TemplateSelection = ({ onSelectTemplate }) => {
  const { templates, isLoading, error, selectedTemplate, selectTemplate } = useTemplateContext();

  const handleTemplateSelect = (template) => {
    selectTemplate(template);
    if (onSelectTemplate) {
      onSelectTemplate(template);
    }
  };

  return (
    <Card title="Выберите шаблон документа">
      {isLoading ? (
        <div className="text-center py-4">{text.TEMPLATE_SELECTION_LOADING}</div>
      ) : error ? (
        <div className="text-red-500 text-center py-4">
          {error}
          <button 
            className="block mx-auto mt-2 text-blue-500 underline"
            onClick={() => window.location.reload()}
          >
            Попробовать снова
          </button>
        </div>
      ) : (
        <TemplateList 
          templates={templates} 
          selectedTemplate={selectedTemplate}
          onSelectTemplate={handleTemplateSelect}
        />
      )}
    </Card>
  );
};

export default TemplateSelection; 