import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchTemplateById, updateTemplate } from '../../api/templateService';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import Select from '../../components/ui/Select';
import { ChevronLeft, Save, FilePlus, Loader2, AlertTriangle, List, Edit } from 'lucide-react';
import { toast } from 'react-hot-toast';

// Добавляем константы
const TPL_EDIT_TITLE = "Редактирование шаблона";
const TPL_EDIT_LOADING = "Загрузка данных шаблона...";
const TPL_EDIT_NOT_FOUND = "Шаблон не найден.";
const TPL_EDIT_LOAD_ERROR = (msg) => `Ошибка загрузки шаблона: ${msg}`;
const TPL_EDIT_UPDATE_SUCCESS = "Шаблон успешно обновлен";
const TPL_EDIT_UPDATE_ERROR = (msg) => `Ошибка обновления шаблона: ${msg}`;
const TPL_EDIT_SAVE_BUTTON = "Сохранить изменения";
const TPL_EDIT_SAVING_BUTTON = "Сохранение...";
const TPL_EDIT_CANCEL_BUTTON = "Отменить";
const TPL_EDIT_SECTION_DETAILS = "Детали шаблона";
const TPL_EDIT_SECTION_PAGES = "Страницы шаблона";
const TPL_EDIT_ADD_PAGE_BUTTON = "Добавить страницу";
const TPL_EDIT_NO_PAGES = "Страницы еще не добавлены.";
const TPL_EDIT_PAGE_DETAILS = (w, h, u, f, a) => `${w}x${h} ${u}, ${f} полей, ${a} ассетов`;
const TPL_EDIT_EDIT_PAGE_BUTTON = "Редактировать страницу";

const TemplateEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { refreshTemplates } = useTemplates();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({ name: '', version: '', type: 'pdf' });

  // useCallback для предотвращения лишних ререндеров
  const loadTemplate = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTemplateById(id);
      setTemplate(data);
      setFormData({ name: data.name, version: data.version, type: data.type });
    } catch (err) {
      console.error('Error loading template:', err);
      setError(TPL_EDIT_LOAD_ERROR(err.message || text.UNKNOWN_ERROR_MSG));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadTemplate();
  }, [loadTemplate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      // TODO: Добавить валидацию
      await updateTemplate(id, formData);
      refreshTemplates(); // Обновляем список в контексте
      toast.success(TPL_EDIT_UPDATE_SUCCESS); // Показываем уведомление
      // Обновляем данные на странице после сохранения
      setTemplate(prev => ({ ...prev, ...formData })); 
    } catch (err) {
      console.error('Failed to update template:', err);
      const errorMsg = TPL_EDIT_UPDATE_ERROR(err.message || text.UNKNOWN_ERROR_MSG);
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };

  const templateTypeOptions = [
    { value: 'pdf', label: 'PDF' },
    { value: 'png', label: 'PNG' },
    { value: 'svg', label: 'SVG' },
  ];

  if (loading) {
    return (
       <div className="flex justify-center items-center h-40">
         <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
         <span className="ml-2 text-gray-600">{TPL_EDIT_LOADING}</span>
       </div>
    );
  }

  // Показываем ошибку загрузки, если шаблон не загружен
  if (error && !template) {
      return (
        <div className="text-center py-10">
           <AlertTriangle className="mx-auto h-12 w-12 text-red-400" />
           <h3 className="mt-2 text-lg font-medium text-red-800">Ошибка</h3>
           <p className="mt-1 text-sm text-red-600">{error}</p>
           <div className="mt-6">
             <Link to="/admin/templates">
               <Button variant="outline">
                 {text.BACK_TO_LIST_BUTTON}
               </Button>
             </Link>
           </div>
         </div>
       );
  }
  
  // Если шаблон не найден после загрузки
  if (!template) {
      return <div className="text-center py-10 text-gray-500">{TPL_EDIT_NOT_FOUND}</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
         <div className="flex items-center gap-3">
            <Link to="/admin/templates" className="text-gray-500 hover:text-gray-700">
                <ChevronLeft size={24}/>
            </Link>
            <h1 className="text-2xl font-semibold text-gray-800">{TPL_EDIT_TITLE}: <span className="font-normal">{template.name}</span></h1>
         </div>
         {/* Можно добавить кнопку "Просмотр" или другие действия */} 
      </div>

      {/* Форма редактирования деталей шаблона */} 
      <Card title={TPL_EDIT_SECTION_DETAILS}>
        <form onSubmit={handleSubmit} className="space-y-6">
           {/* Показываем ошибку сохранения */} 
           {error && !loading && (
             <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md text-sm" role="alert">
               {error}
             </div>
           )}
          <Input
            label={text.TPL_CREATE_NAME_LABEL} // Используем константы из Create
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <Input
            label={text.TPL_CREATE_VERSION_LABEL}
            id="version"
            name="version"
            value={formData.version}
            onChange={handleChange}
            required
          />
          <Select
             label={text.TPL_CREATE_TYPE_LABEL}
             id="type"
             name="type"
             value={formData.type}
             onChange={handleChange}
             options={templateTypeOptions}
             required
           />
          <div className="pt-4 flex justify-end space-x-3 border-t border-gray-200">
             {/* Кнопка отмены может просто сбрасывать изменения */} 
             <Button
               type="button"
               variant="outline"
               onClick={() => setFormData({ name: template.name, version: template.version, type: template.type })} // Сброс
               disabled={saving}
             >
               {TPL_EDIT_CANCEL_BUTTON}
             </Button>
             <Button
               type="submit"
               isLoading={saving}
               icon={<Save size={16}/>}
             >
               {saving ? TPL_EDIT_SAVING_BUTTON : TPL_EDIT_SAVE_BUTTON}
             </Button>
          </div>
        </form>
      </Card>

      {/* Секция управления страницами */} 
      <Card 
         title={TPL_EDIT_SECTION_PAGES}
         titleRight={
             <Link to={`/admin/templates/${id}/pages/new`}>
               <Button variant="default" size="sm" icon={<FilePlus size={16}/>}>
                 {TPL_EDIT_ADD_PAGE_BUTTON}
               </Button>
             </Link>
         }
      >
         {template.pages?.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              {TPL_EDIT_NO_PAGES}
            </div>
          ) : (
            <ul className="divide-y divide-gray-200 -mx-6"> {/* Убираем отступы Card */} 
              {template.pages?.map((page) => (
                <li key={page.name} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
                   <div className="flex items-center space-x-3">
                       <List className="text-gray-400"/> {/* Иконка страницы */} 
                       <div>
                         <h4 className="text-sm font-medium text-gray-900">{page.name}</h4>
                         <p className="text-xs text-gray-500">
                            {TPL_EDIT_PAGE_DETAILS(
                                page.width, 
                                page.height, 
                                page.units, 
                                page.fields?.length || 0, 
                                page.assets?.length || 0
                            )}
                         </p>
                       </div>
                   </div>
                  <Link
                    to={`/admin/templates/${id}/pages/${page.name}`} // TODO: Убедиться, что ID страницы это name
                    title={TPL_EDIT_EDIT_PAGE_BUTTON}
                  >
                    <Button variant="ghost" size="sm" icon={<Edit size={16}/>} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
      </Card>
    </div>
  );
};

export default TemplateEdit; 