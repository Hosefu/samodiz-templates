import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { createPage } from '../../api/pageService';
import * as text from '../../constants/ux-writing';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import Select from '../../components/ui/Select';
import Checkbox from '../../components/ui/Checkbox';
import CodeEditor from '../../components/admin/CodeEditor';
import { ChevronLeft, Save, PlusCircle, Trash2 } from 'lucide-react';
import { toast } from 'react-hot-toast';

// Локальные константы для страницы
const PAGE_CREATE_TITLE = "Создание новой страницы";
const PAGE_CREATE_DESCRIPTION = (templateId) => `Добавление страницы к шаблону ID: ${templateId}`;
const PAGE_CREATE_ERROR = (msg) => `Не удалось создать страницу: ${msg}`;
const PAGE_CREATE_SUBMIT_BUTTON = "Создать страницу";
const PAGE_CREATE_SUBMITTING_BUTTON = "Создание...";
const PAGE_CREATE_CANCEL_BUTTON = "Отмена";
const PAGE_CREATE_SECTION_DETAILS = "Детали страницы";
const PAGE_CREATE_SECTION_HTML = "HTML разметка страницы";
const PAGE_CREATE_SECTION_FIELDS = "Поля шаблона (переменные)";
const PAGE_CREATE_FIELD_NAME_LABEL = "Название поля (переменной)";
const PAGE_CREATE_FIELD_NAME_PLACEHOLDER = "например, client_name";
const PAGE_CREATE_FIELD_LABEL_LABEL = "Метка поля (для формы)";
const PAGE_CREATE_FIELD_LABEL_PLACEHOLDER = "Например, Имя клиента";
const PAGE_CREATE_FIELD_REQUIRED_LABEL = "Обязательное";
const PAGE_CREATE_ADD_FIELD_BUTTON = "Добавить поле";
const PAGE_CREATE_DELETE_FIELD_BUTTON = "Удалить поле";
const PAGE_CREATE_NAME_LABEL = "Название страницы (ID)";
const PAGE_CREATE_WIDTH_LABEL = "Ширина";
const PAGE_CREATE_HEIGHT_LABEL = "Высота";
const PAGE_CREATE_UNITS_LABEL = "Единицы изм.";
const PAGE_CREATE_BLEEDS_LABEL = "Вылеты (bleeds)";
const PAGE_CREATE_UNITS_OPTIONS = [
  { value: 'mm', label: 'Миллиметры (mm)' },
  { value: 'px', label: 'Пиксели (px)' },
];
const PAGE_CREATE_DEFAULT_HTML = `<!DOCTYPE html>
<html>
<head>
  <title>Page Template</title>
  <style>
    /* Стили для PDF рендеринга */
    body { font-family: sans-serif; margin: 0; }
    .content { padding: 20mm; } 
    /* Добавляйте ваши стили здесь */ 
  </style>
</head>
<body>
  <div class="content">
    <h1>{{title}}</h1>
    <p>Hello, {{name}}!</p>
  </div>
</body>
</html>`;

const PageCreate = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    width: 210,
    height: 297,
    units: 'mm',
    bleeds: 3,
    html: PAGE_CREATE_DEFAULT_HTML
  });
  // Начальные поля по умолчанию из HTML
  const [fields, setFields] = useState([
    { name: 'title', label: text.PAGE_CREATE_FIELD_DEFAULT_TITLE, required: true },
    { name: 'name', label: text.PAGE_CREATE_FIELD_DEFAULT_NAME, required: true }
  ]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value // Используем parseFloat
    }));
    setError(null); // Сброс ошибки при изменении
  };

  const handleHtmlChange = (newValue) => {
    setFormData(prev => ({ ...prev, html: newValue }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // TODO: Валидация данных (особенно уникальность имени)
      const pageData = {
        ...formData,
        fields,
        assets: [] // Assets пока не реализованы
      };
      
      const newPage = await createPage(templateId, pageData);
      toast.success(`Страница "${newPage.name}" успешно создана!`);
      // Переходим на страницу редактирования созданного шаблона
      navigate(`/admin/templates/${templateId}`); 
    } catch (err) {
      console.error('Failed to create page:', err);
      const errorMsg = PAGE_CREATE_ERROR(err.response?.data?.detail || err.message || text.UNKNOWN_ERROR_MSG);
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleAddField = () => {
    setFields([...fields, { name: '', label: '', required: false }]);
  };

  const handleFieldChange = (index, fieldData) => {
    const updatedFields = [...fields];
    updatedFields[index] = fieldData;
    setFields(updatedFields);
  };

  const handleDeleteField = (index) => {
    const updatedFields = fields.filter((_, i) => i !== index);
    setFields(updatedFields);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
       <div className="flex items-center justify-between">
         <div className="flex items-center gap-3">
            <Link to={`/admin/templates/${templateId}`} className="text-gray-500 hover:text-gray-700">
                <ChevronLeft size={24}/>
            </Link>
            <div>
                <h1 className="text-2xl font-semibold text-gray-800">{PAGE_CREATE_TITLE}</h1>
                <p className="text-sm text-gray-500">{PAGE_CREATE_DESCRIPTION(templateId)}</p>
            </div>
         </div>
         <div className="flex space-x-3">
            <Link to={`/admin/templates/${templateId}`}>
                <Button type="button" variant="outline" disabled={loading}>
                    {PAGE_CREATE_CANCEL_BUTTON}
                </Button>
             </Link>
             <Button type="submit" isLoading={loading} icon={<Save size={16} />}>
               {loading ? PAGE_CREATE_SUBMITTING_BUTTON : PAGE_CREATE_SUBMIT_BUTTON}
             </Button>
         </div>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md text-sm" role="alert">
          {error}
        </div>
      )}

      {/* Детали страницы */}
      <Card title={PAGE_CREATE_SECTION_DETAILS}>
        <div className="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
             <Input
                label={PAGE_CREATE_NAME_LABEL}
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                // TODO: Добавить валидацию на уникальность имени
              />
          </div>
           <div className="sm:col-span-1">
             <Input
                label={PAGE_CREATE_WIDTH_LABEL}
                id="width"
                name="width"
                type="number"
                value={formData.width}
                onChange={handleChange}
                required min="1"
              />
          </div>
          <div className="sm:col-span-1">
            <Input
                label={PAGE_CREATE_HEIGHT_LABEL}
                id="height"
                name="height"
                type="number"
                value={formData.height}
                onChange={handleChange}
                required min="1"
              />
          </div>
           <div className="sm:col-span-1">
            <Select
               label={PAGE_CREATE_UNITS_LABEL}
               id="units"
               name="units"
               value={formData.units}
               onChange={handleChange}
               options={PAGE_CREATE_UNITS_OPTIONS}
               required
             />
          </div>
           <div className="sm:col-span-2">
            <Input
               label={PAGE_CREATE_BLEEDS_LABEL}
               id="bleeds"
               name="bleeds"
               type="number"
               value={formData.bleeds}
               onChange={handleChange}
               min="0"
               hint="Отступы под обрез (в выбранных единицах)"
             />
          </div>
        </div>
      </Card>

      {/* Редактор HTML */}
      <Card title={PAGE_CREATE_SECTION_HTML}>
        <CodeEditor
          value={formData.html}
          onChange={handleHtmlChange}
          language="html"
          height="400px"
        />
      </Card>

      {/* Поля шаблона */}
      <Card 
         title={PAGE_CREATE_SECTION_FIELDS}
         titleRight={
             <Button type="button" variant="outline" size="sm" onClick={handleAddField} icon={<PlusCircle size={16}/>}>
                 {PAGE_CREATE_ADD_FIELD_BUTTON}
             </Button>
         }
      >
         {fields.length === 0 ? (
            <p className="text-center text-gray-500 py-4">{text.HOME_NO_FIELDS_IN_TEMPLATE}</p>
         ) : (
            <div className="space-y-4">
              {fields.map((field, index) => (
                <div key={index} className="grid grid-cols-1 gap-4 sm:grid-cols-8 items-end border-b border-gray-100 pb-4">
                  <div className="sm:col-span-3">
                     <Input
                       label={PAGE_CREATE_FIELD_NAME_LABEL}
                       value={field.name}
                       onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })}
                       placeholder={PAGE_CREATE_FIELD_NAME_PLACEHOLDER}
                       required
                     />
                  </div>
                  <div className="sm:col-span-3">
                    <Input
                       label={PAGE_CREATE_FIELD_LABEL_LABEL}
                       value={field.label}
                       onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })}
                       placeholder={PAGE_CREATE_FIELD_LABEL_PLACEHOLDER}
                       required
                     />
                  </div>
                  <div className="sm:col-span-1 flex items-center pt-5"> {/* Выравниваем по вертикали */}
                     <Checkbox
                       id={`required-${index}`}
                       checked={field.required}
                       onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })}
                       label={PAGE_CREATE_FIELD_REQUIRED_LABEL}
                     />
                  </div>
                  <div className="sm:col-span-1 flex justify-end pt-5"> {/* Кнопка справа */} 
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      icon={<Trash2 className="text-red-600" />} 
                      onClick={() => handleDeleteField(index)}
                      title={PAGE_CREATE_DELETE_FIELD_BUTTON}
                    />
                  </div>
                </div>
              ))}
            </div>
         )}
      </Card>
       {/* Нижние кнопки сохранения/отмены */}
       <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Link to={`/admin/templates/${templateId}`}>
                <Button type="button" variant="outline" disabled={loading}>
                    {PAGE_CREATE_CANCEL_BUTTON}
                </Button>
             </Link>
             <Button type="submit" isLoading={loading} icon={<Save size={16} />}>
               {loading ? PAGE_CREATE_SUBMITTING_BUTTON : PAGE_CREATE_SUBMIT_BUTTON}
             </Button>
         </div>
    </form>
  );
};

export default PageCreate; 