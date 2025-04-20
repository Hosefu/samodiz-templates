import React, { useState, useEffect } from 'react';
import { Camera, CheckCircle, ChevronLeft, ChevronRight, Download, FileText, Loader2 } from 'lucide-react';

// Компоненты UI
const Button = ({ children, variant = 'default', size = 'default', disabled = false, onClick, className = '', icon }) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variantClasses = {
    default: 'bg-blue-500 text-white hover:bg-blue-600',
    outline: 'border border-slate-200 hover:bg-slate-100 hover:text-slate-900',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
    ghost: 'hover:bg-slate-100 hover:text-slate-900',
    link: 'text-blue-500 underline-offset-4 hover:underline',
  };
  
  const sizeClasses = {
    default: 'h-10 py-2 px-4',
    sm: 'h-8 px-3 text-sm',
    lg: 'h-12 px-8 text-lg',
    icon: 'h-10 w-10',
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  return (
    <button className={classes} disabled={disabled} onClick={onClick}>
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
};

const Card = ({ children, title, className = '' }) => (
  <div className={`bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden ${className}`}>
    {title && (
      <div className="border-b border-slate-200 p-4 font-medium">
        {title}
      </div>
    )}
    <div className="p-4">
      {children}
    </div>
  </div>
);

const Input = ({ label, name, value, onChange, required = false, type = 'text', placeholder = '' }) => (
  <div className="mb-4">
    <label htmlFor={name} className="block text-sm font-medium text-slate-700 mb-1">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    <input
      type={type}
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      required={required}
      placeholder={placeholder}
      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

const TemplateCard = ({ template, selected, onClick }) => (
  <div 
    className={`border rounded-lg p-4 cursor-pointer transition-colors ${selected ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-blue-300'}`}
    onClick={onClick}
  >
    <div className="flex justify-between items-center">
      <div>
        <h3 className="font-medium text-slate-900">{template.name}</h3>
        <p className="text-sm text-slate-500">Версия: {template.version}</p>
        <div className="flex items-center mt-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {template.type.toUpperCase()}
          </span>
          <span className="ml-2 text-xs text-slate-500">{template.pages.length} страниц</span>
        </div>
      </div>
      {selected && (
        <CheckCircle className="text-blue-500 h-6 w-6" />
      )}
    </div>
  </div>
);

// Основное приложение
const App = () => {
  // Состояния
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [formData, setFormData] = useState({});
  const [currentStep, setCurrentStep] = useState(0);
  const [activePage, setActivePage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedFileUrl, setGeneratedFileUrl] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Получение списка шаблонов при загрузке
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/templates');
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      const data = await response.json();
      setTemplates(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setCurrentStep(1);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePageChange = (pageIndex) => {
    setActivePage(pageIndex);
  };

  const handleGenerate = async () => {
    if (!validateForm()) return;

    try {
      setIsLoading(true);
      const response = await fetch('/api/render/template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          data: formData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate document');
      }

      const data = await response.json();
      setGeneratedFileUrl(data.url);
      setPreviewUrl(data.previewUrl);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    if (!selectedTemplate) return false;
    
    const requiredFields = selectedTemplate.fields.filter(field => field.required);
    return requiredFields.every(field => formData[field.name]);
  };

  // Рендеринг шагов
  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map(template => (
              <TemplateCard
                key={template.id}
                template={template}
                selected={selectedTemplate?.id === template.id}
                onClick={() => handleTemplateSelect(template)}
              />
            ))}
          </div>
        );
      case 1:
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Заполните данные</h2>
              <Button
                variant="outline"
                onClick={() => setCurrentStep(0)}
                icon={<ChevronLeft className="h-4 w-4" />}
              >
                Назад
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {selectedTemplate.fields.map(field => (
                <Input
                  key={field.name}
                  label={field.label}
                  name={field.name}
                  value={formData[field.name] || ''}
                  onChange={handleFormChange}
                  required={field.required}
                  type={field.type}
                  placeholder={field.placeholder}
                />
              ))}
            </div>
            <div className="flex justify-end">
              <Button
                onClick={handleGenerate}
                disabled={isLoading || !validateForm()}
                icon={isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              >
                {isLoading ? 'Генерация...' : 'Сгенерировать'}
              </Button>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Результат</h2>
              <Button
                variant="outline"
                onClick={() => setCurrentStep(0)}
                icon={<ChevronLeft className="h-4 w-4" />}
              >
                Назад
              </Button>
            </div>
            {previewUrl && (
              <div className="aspect-[3/4] w-full max-w-2xl mx-auto">
                <iframe
                  src={previewUrl}
                  className="w-full h-full border border-slate-200 rounded-lg"
                  title="Preview"
                />
              </div>
            )}
            <div className="flex justify-center gap-4">
              <Button
                variant="default"
                onClick={() => window.open(generatedFileUrl, '_blank')}
                icon={<Download className="h-4 w-4" />}
              >
                Скачать
              </Button>
              <Button
                variant="outline"
                onClick={() => setCurrentStep(0)}
              >
                Новый документ
              </Button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="container mx-auto px-4">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Генератор документов</h1>
          <p className="text-slate-600 mt-2">Выберите шаблон и заполните необходимые данные</p>
        </header>

        <main>
          <Card>
            {error ? (
              <div className="text-red-500 text-center py-4">
                {error}
              </div>
            ) : (
              renderStep()
            )}
          </Card>
        </main>
      </div>
    </div>
  );
};

export default App;