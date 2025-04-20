import React, { createContext, useContext, useState } from 'react';
import { useFormData } from '../hooks';

const FormContext = createContext();

export const FormProvider = ({ children }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const { formData, errors, handleChange, validate, resetForm: resetFormData, setFormData } = useFormData({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState(null);

  const goToNextStep = () => {
    setCurrentStep(prev => prev + 1);
  };

  const goToPrevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  const resetForm = () => {
    setCurrentStep(0);
    resetFormData();
    setGeneratedDoc(null);
  };

  const generateDocument = async (templateId) => {
    try {
      setIsSubmitting(true);
      const response = await fetch('/api/render/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          data: formData,
        }),
      });

      if (!response.ok) {
        throw new Error('Не удалось сгенерировать документ');
      }

      const data = await response.json();
      setGeneratedDoc(data);
      goToNextStep();
      return data;
    } catch (error) {
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <FormContext.Provider
      value={{
        currentStep,
        formData,
        errors,
        isSubmitting,
        generatedDoc,
        handleChange,
        validate,
        goToNextStep,
        goToPrevStep,
        resetForm,
        setFormData,
        generateDocument,
      }}
    >
      {children}
    </FormContext.Provider>
  );
};

export const useFormContext = () => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useFormContext must be used within a FormProvider');
  }
  return context;
}; 