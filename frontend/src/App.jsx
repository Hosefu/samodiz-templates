import React, { useState, useEffect } from 'react';
import { Camera, CheckCircle, ChevronLeft, ChevronRight, Download, FileText, Loader2 } from 'lucide-react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import './App.css';

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

// Простые компоненты для тестирования
const Home = () => <div className="p-8">Главная страница</div>;
const Login = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const handleLogin = async (e) => {
    e.preventDefault();
    await login(username, password);
  };
  
  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">Вход в систему</h1>
      <form onSubmit={handleLogin} className="space-y-4 max-w-md">
        <div>
          <label className="block mb-1">Имя пользователя:</label>
          <input 
            type="text" 
            value={username} 
            onChange={e => setUsername(e.target.value)}
            className="w-full p-2 border rounded" 
          />
        </div>
        <div>
          <label className="block mb-1">Пароль:</label>
          <input 
            type="password" 
            value={password} 
            onChange={e => setPassword(e.target.value)}
            className="w-full p-2 border rounded" 
          />
        </div>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">
          Войти
        </button>
      </form>
    </div>
  );
};

const Admin = () => {
  const { isAuthenticated, user } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (user && user.isAdmin) {
    window.location.href = '/admin.html';
    return null;
  }
  
  return <div className="p-8">У вас нет прав для доступа к административной панели</div>;
};

// Диагностический компонент
const Diagnostics = () => {
  const { user, isAuthenticated, authError } = useAuth();
  const location = useLocation();
  const [apiStatus, setApiStatus] = useState('Проверка...');
  
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch('/api/health/');
        if (response.ok) {
          setApiStatus('API доступен');
        } else {
          setApiStatus(`API недоступен: ${response.status} ${response.statusText}`);
        }
      } catch (error) {
        setApiStatus(`Ошибка подключения к API: ${error.message}`);
      }
    };
    
    checkApi();
  }, []);
  
  return (
    <div className="diagnostics" style={{ 
      position: 'fixed', 
      bottom: '10px', 
      right: '10px',
      backgroundColor: '#f8f9fa',
      border: '1px solid #ddd',
      borderRadius: '4px',
      padding: '10px',
      zIndex: 9999,
      maxWidth: '400px',
      fontSize: '12px'
    }}>
      <h3 style={{margin: '0 0 5px 0'}}>Диагностика</h3>
      <div>Текущий путь: <strong>{location.pathname}</strong></div>
      <div>Аутентификация: <strong>{isAuthenticated ? 'Да' : 'Нет'}</strong></div>
      <div>API статус: <strong>{apiStatus}</strong></div>
      {authError && <div style={{color: 'red'}}>Ошибка: {authError}</div>}
      {user && <div>Пользователь: {user.username}</div>}
    </div>
  );
};

// Навигация
const Navigation = () => {
  const { isAuthenticated, logout } = useAuth();
  
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="font-bold text-xl">Документ Генератор</div>
        <ul className="flex space-x-4">
          <li><Link to="/" className="hover:text-gray-300">Главная</Link></li>
          {isAuthenticated ? (
            <>
              <li><Link to="/admin" className="hover:text-gray-300">Админ</Link></li>
              <li><button onClick={logout} className="hover:text-gray-300">Выход</button></li>
            </>
          ) : (
            <li><Link to="/login" className="hover:text-gray-300">Вход</Link></li>
          )}
        </ul>
      </div>
    </nav>
  );
};

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

  // Переход на админку
  const goToAdmin = () => {
    window.location.href = '/admin/';
  };

  // Получение списка шаблонов при загрузке
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/templates/');
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      const data = await response.json();
      console.log('Fetched templates:', data); // Debug log
      setTemplates(data);
    } catch (err) {
      console.error('Error fetching templates:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    console.log('Selected template:', template); // Debug log
    setSelectedTemplate(template);
    setCurrentStep(1);
    // Reset form data when selecting a new template
    setFormData({});
    // Reset active page when selecting a new template
    setActivePage(0);
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
      const response = await fetch('/api/render/generate', {
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
      console.error('Error generating document:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    if (!selectedTemplate) return false;
    
    // Get all required fields across all pages
    const requiredFields = selectedTemplate.pages
      .flatMap(page => page.fields || [])
      .filter(field => field.required)
      .map(field => field.name);
    
    return requiredFields.every(fieldName => formData[fieldName] && formData[fieldName].trim() !== '');
  };

  // Collect all fields from all pages
  const getAllFields = () => {
    if (!selectedTemplate || !selectedTemplate.pages) return [];
    
    return selectedTemplate.pages.flatMap(page => page.fields || []);
  };

  // Рендеринг шагов
  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <>
            <div className="flex justify-end mb-4">
              <Button
                variant="outline"
                onClick={goToAdmin}
                className="mb-4"
              >
                Перейти в админку
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(templates || []).map(template => (
                <TemplateCard
                  key={template.id}
                  template={template}
                  selected={selectedTemplate?.id === template.id}
                  onClick={() => handleTemplateSelect(template)}
                />
              ))}
            </div>
          </>
        );
      case 1:
        // Added error handling for when template structure is invalid
        if (!selectedTemplate || !selectedTemplate.pages) {
          return (
            <div className="text-red-500 text-center py-4">
              Invalid template structure. Please select another template.
            </div>
          );
        }
        
        const fields = getAllFields();
        
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
              {fields.map(field => (
                <Input
                  key={field.name}
                  label={field.label}
                  name={field.name}
                  value={formData[field.name] || ''}
                  onChange={handleFormChange}
                  required={field.required}
                  type="text"
                  placeholder={field.label}
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
    <>
      <Diagnostics />
      <Navigation />
      
      <div className="container mx-auto p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </>
  );
};

export default App;