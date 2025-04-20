import React, { useState } from 'react';
import { Button, Input } from '../ui';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const TemplateForm = ({ template, initialData = {}, onSubmit, onBack, isSubmitting }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});

  const pages = template.pages || [];
  const isLastPage = currentPage === pages.length - 1;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when field is updated
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validatePage = () => {
    const currentFields = pages[currentPage]?.fields || [];
    const requiredFields = currentFields.filter(field => field.required).map(field => field.name);
    
    const newErrors = {};
    let isValid = true;

    requiredFields.forEach(field => {
      if (!formData[field] || formData[field].trim() === '') {
        newErrors[field] = 'Это поле обязательно';
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleNext = () => {
    if (validatePage()) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentPage(prev => prev - 1);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validatePage()) {
      onSubmit(formData);
    }
  };

  if (!pages.length) {
    return <div>Шаблон не содержит страниц</div>;
  }

  const currentFields = pages[currentPage]?.fields || [];

  return (
    <form onSubmit={isLastPage ? handleSubmit : (e) => e.preventDefault()}>
      <div className="space-y-6">
        {pages.length > 1 && (
          <div className="flex justify-between items-center mb-4">
            <div className="text-sm font-medium">
              Страница {currentPage + 1} из {pages.length}
            </div>
            <div className="text-sm text-slate-500">
              {pages[currentPage]?.title || `Шаг ${currentPage + 1}`}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentFields.map(field => (
            <Input
              key={field.name}
              label={field.label}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={handleChange}
              required={field.required}
              type={field.type || 'text'}
              placeholder={field.placeholder || ''}
              error={errors[field.name]}
            />
          ))}
        </div>
        
        <div className="flex justify-between pt-4">
          <Button 
            variant="outline" 
            onClick={currentPage === 0 ? onBack : handlePrevious}
            icon={<ChevronLeft className="h-4 w-4" />}
          >
            {currentPage === 0 ? 'Назад к шаблонам' : 'Назад'}
          </Button>
          
          {isLastPage ? (
            <Button 
              type="submit" 
              disabled={isSubmitting}
              isLoading={isSubmitting}
            >
              Сгенерировать
            </Button>
          ) : (
            <Button 
              onClick={handleNext}
              icon={<ChevronRight className="h-4 w-4" />}
              iconPosition="right"
            >
              Далее
            </Button>
          )}
        </div>
      </div>
    </form>
  );
};

export default TemplateForm; 