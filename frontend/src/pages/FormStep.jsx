import React from 'react';
import { Card } from '../components/ui';
import { TemplateForm } from '../components/forms';
import { useTemplateContext } from '../context/TemplateContext';
import { useFormContext } from '../context/FormContext';

const FormStep = ({ onBack }) => {
  const { selectedTemplate } = useTemplateContext();
  const { formData, isSubmitting, generateDocument } = useFormContext();

  const handleSubmit = async (data) => {
    try {
      await generateDocument(selectedTemplate.id);
    } catch (error) {
      console.error('Failed to generate document:', error);
      // Handle error case
    }
  };

  if (!selectedTemplate) {
    return (
      <Card>
        <div className="text-center py-4">
          Шаблон не выбран. <button className="text-blue-500" onClick={onBack}>Вернуться к выбору шаблона</button>
        </div>
      </Card>
    );
  }

  return (
    <Card title={`Заполнение шаблона: ${selectedTemplate.name}`}>
      <TemplateForm
        template={selectedTemplate}
        initialData={formData}
        onSubmit={handleSubmit}
        onBack={onBack}
        isSubmitting={isSubmitting}
      />
    </Card>
  );
};

export default FormStep; 