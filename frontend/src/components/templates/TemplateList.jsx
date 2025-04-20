import React from 'react';
import TemplateCard from './TemplateCard';

const TemplateList = ({ templates, selectedTemplate, onSelectTemplate }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map(template => (
        <TemplateCard
          key={template.id}
          template={template}
          selected={selectedTemplate && selectedTemplate.id === template.id}
          onClick={() => onSelectTemplate(template)}
        />
      ))}
      {templates.length === 0 && (
        <div className="col-span-3 text-center py-8 text-slate-500">
          Шаблоны не найдены
        </div>
      )}
    </div>
  );
};

export default TemplateList; 