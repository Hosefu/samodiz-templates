import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { fetchTemplateById } from '../../api/templateService'; // Fetch template details
import { updatePage } from '../../api/pageService';
import { uploadAsset, deleteAsset } from '../../api/assetService';
import * as text from '../../constants/ux-writing';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import Select from '../../components/ui/Select';
import Checkbox from '../../components/ui/Checkbox';
import CodeEditor from '../../components/admin/CodeEditor';
import FileUploader from '../../components/admin/FileUploader';
import Modal from '../../components/ui/Modal';
import { ChevronLeft, Save, PlusCircle, Trash2, Loader2, AlertTriangle, UploadCloud, Copy, ExternalLink, Image as ImageIcon } from 'lucide-react';
import { toast } from 'react-hot-toast';

// Локальные константы
const PAGE_EDIT_TITLE = "Редактирование страницы";
const PAGE_EDIT_LOADING = "Загрузка данных страницы...";
const PAGE_EDIT_NOT_FOUND = "Страница не найдена в этом шаблоне.";
const PAGE_EDIT_LOAD_ERROR = (msg) => `Ошибка загрузки страницы: ${msg}`;
const PAGE_EDIT_UPDATE_SUCCESS = "Страница успешно обновлена";
const PAGE_EDIT_UPDATE_ERROR = (msg) => `Ошибка обновления страницы: ${msg}`;
const PAGE_EDIT_SAVE_BUTTON = "Сохранить страницу";
const PAGE_EDIT_SAVING_BUTTON = "Сохранение...";
const PAGE_EDIT_CANCEL_BUTTON = "Отмена"; // Или "Вернуться к шаблону"
const PAGE_EDIT_SECTION_DETAILS = "Детали страницы";
const PAGE_EDIT_SECTION_HTML = "HTML разметка";
const PAGE_EDIT_SECTION_FIELDS = "Поля (переменные)";
const PAGE_EDIT_SECTION_ASSETS = "Ассеты (изображения, шрифты)";
const PAGE_EDIT_ADD_FIELD_BUTTON = "Добавить поле";
const PAGE_EDIT_DELETE_FIELD_BUTTON = "Удалить поле";
const PAGE_EDIT_FIELD_REQUIRED_LABEL = "Обяз."; // Короткая метка
const PAGE_EDIT_UPLOAD_ASSET_BUTTON = "Загрузить ассет";
const PAGE_EDIT_DELETE_ASSET_BUTTON = "Удалить ассет";
const PAGE_EDIT_COPY_ASSET_PATH_BUTTON = "Копировать путь";
const PAGE_EDIT_ASSET_PATH_COPIED = "Путь скопирован!";
const PAGE_EDIT_CONFIRM_DELETE_ASSET_TITLE = "Подтвердите удаление";
const PAGE_EDIT_CONFIRM_DELETE_ASSET_MSG = (name) => `Вы уверены, что хотите удалить ассет "${name}"? Использующие его шаблоны могут сломаться.`;
const PAGE_EDIT_DELETE_ASSET_ERROR = (msg) => `Ошибка удаления ассета: ${msg}`;

const PageEdit = () => {
  const { templateId, pageId } = useParams();
  const navigate = useNavigate();
  const [templateName, setTemplateName] = useState(''); // Храним имя шаблона для хлебных крошек
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [formError, setFormError] = useState(null); // Ошибка для формы
  const [formData, setFormData] = useState({ name: '', width: 210, height: 297, units: 'mm', bleeds: 3, html: '' });
  const [fields, setFields] = useState([]);
  // Состояния для модального окна удаления ассета
  const [showDeleteAssetConfirm, setShowDeleteAssetConfirm] = useState(false);
  const [assetToDelete, setAssetToDelete] = useState(null);
  const [deleteAssetError, setDeleteAssetError] = useState(null);
  const [isDeletingAsset, setIsDeletingAsset] = useState(false);

  // Загрузка данных
  const loadPageData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setFormError(null);
      const templateData = await fetchTemplateById(templateId);
      setTemplateName(templateData.name);
      const pageData = templateData.pages.find(p => p.name === pageId);
      if (pageData) {
        setPage(pageData);
        setFormData({
          name: pageData.name,
          width: pageData.width,
          height: pageData.height,
          units: pageData.units,
          bleeds: pageData.bleeds,
          html: pageData.html
        });
        setFields(pageData.fields || []);
      } else {
        setError(PAGE_EDIT_NOT_FOUND);
      }
    } catch (err) {
      console.error('Error loading page data:', err);
      setError(PAGE_EDIT_LOAD_ERROR(err.message || text.UNKNOWN_ERROR_MSG));
    } finally {
      setLoading(false);
    }
  }, [templateId, pageId]);

  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  // Обработчики изменений формы
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
    setFormError(null); // Сброс ошибки формы при изменении
  };

  const handleHtmlChange = (newValue) => {
    setFormData(prev => ({ ...prev, html: newValue }));
  };

  // Обработчики полей
  const handleAddField = () => {
    setFields([...fields, { name: '', label: '', required: false }]);
  };

  const handleFieldChange = (index, fieldData) => {
    const updatedFields = [...fields];
    updatedFields[index] = fieldData;
    setFields(updatedFields);
  };

  const handleDeleteField = (index) => {
    setFields(fields.filter((_, i) => i !== index));
  };

  // Обработчики ассетов
  const handleFileUpload = async (file) => {
    try {
      const asset = await uploadAsset(templateId, pageId, file);
      setPage(prev => ({
        ...prev,
        assets: [...(prev.assets || []), asset]
      }));
      toast.success(`Ассет "${asset.name || text.ASSET_NAME_DEFAULT}" загружен.`);
    } catch (err) {
      console.error('Failed to upload file:', err);
      toast.error(err.response?.data?.detail || text.UPLOAD_FILE_FAILED_MSG);
    }
  };

  const openDeleteAssetConfirm = (asset) => {
    setAssetToDelete(asset);
    setShowDeleteAssetConfirm(true);
    setDeleteAssetError(null);
  };

  const closeDeleteAssetConfirm = () => {
    setShowDeleteAssetConfirm(false);
    setAssetToDelete(null);
  };

  const handleDeleteAsset = async () => {
    if (!assetToDelete) return;
    setIsDeletingAsset(true);
    setDeleteAssetError(null);
    try {
      await deleteAsset(templateId, pageId, assetToDelete.id);
      setPage(prev => ({
        ...prev,
        assets: prev.assets.filter(a => a.id !== assetToDelete.id)
      }));
      toast.success(`Ассет "${assetToDelete.name || text.ASSET_NAME_DEFAULT}" удален.`);
      closeDeleteAssetConfirm();
    } catch (err) {
      console.error('Failed to delete asset:', err);
      const errorMsg = PAGE_EDIT_DELETE_ASSET_ERROR(err.message || text.UNKNOWN_ERROR_MSG);
      setDeleteAssetError(errorMsg);
    } finally {
      setIsDeletingAsset(false);
    }
  };
  
  const copyAssetPath = (path) => {
      navigator.clipboard.writeText(path)
         .then(() => toast.success(PAGE_EDIT_ASSET_PATH_COPIED))
         .catch(err => toast.error(text.COPY_PATH_FAILED_MSG));
  };

  // Сохранение страницы
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      // TODO: Валидация
      const pageData = {
        ...formData,
        fields,
        assets: page.assets || []
      };
      
      await updatePage(templateId, pageId, pageData);
      // Обновляем локальное состояние страницы после успешного сохранения
      setPage(prev => ({ ...prev, ...pageData })); 
      toast.success(PAGE_EDIT_UPDATE_SUCCESS);
    } catch (err) {
      console.error('Failed to update page:', err);
      const errorMsg = PAGE_EDIT_UPDATE_ERROR(err.response?.data?.detail || err.message || text.UNKNOWN_ERROR_MSG);
      setFormError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };
  
   const pageUnitsOptions = [
     { value: 'mm', label: 'Миллиметры (mm)' },
     { value: 'px', label: 'Пиксели (px)' },
   ];

  // Рендеринг
  if (loading) {
    return (
       <div className="flex justify-center items-center h-40">
         <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
         <span className="ml-2 text-gray-600">{PAGE_EDIT_LOADING}</span>
       </div>
    );
  }

  if (error && !page) {
      return (
        <div className="text-center py-10">
           <AlertTriangle className="mx-auto h-12 w-12 text-red-400" />
           <h3 className="mt-2 text-lg font-medium text-red-800">Ошибка</h3>
           <p className="mt-1 text-sm text-red-600">{error}</p>
           <div className="mt-6">
             <Link to={`/admin/templates/${templateId}`}>
               <Button variant="outline">
                 {text.BACK_TO_LIST_BUTTON}
               </Button>
             </Link>
           </div>
         </div>
       );
  }

  if (!page) {
      return <div className="text-center py-10 text-gray-500">{PAGE_EDIT_NOT_FOUND}</div>;
  }

  return (
     // Обертка в форму, чтобы кнопки внизу работали
    <form onSubmit={handleSubmit} className="space-y-8">
       {/* Хлебные крошки и кнопки */} 
      <div className="flex items-center justify-between">
         <div className="flex items-center gap-3">
            <Link to={`/admin/templates/${templateId}`} className="text-gray-500 hover:text-gray-700" title={`К шаблону "${templateName}"`}>
                <ChevronLeft size={24}/>
            </Link>
             <h1 className="text-2xl font-semibold text-gray-800">{PAGE_EDIT_TITLE}: <span className="font-normal">{page.name}</span></h1>
         </div>
         <div className="flex space-x-3">
            {/* Отмена просто возвращает к шаблону */}
            <Link to={`/admin/templates/${templateId}`}>
                <Button type="button" variant="outline" disabled={saving}>
                    {PAGE_EDIT_CANCEL_BUTTON}
                </Button>
             </Link>
             <Button type="submit" isLoading={saving} icon={<Save size={16} />}>
               {saving ? PAGE_EDIT_SAVING_BUTTON : PAGE_EDIT_SAVE_BUTTON}
             </Button>
         </div>
      </div>

       {/* Общая ошибка формы */} 
       {formError && (
         <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md text-sm" role="alert">
           {formError}
         </div>
       )}
       
       {/* Детали страницы */} 
       <Card title={PAGE_EDIT_SECTION_DETAILS}>
         <div className="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
           {/* Поле Name не редактируется, т.к. используется как ID */}
           <div className="sm:col-span-3">
             <Input
                label={text.PAGE_CREATE_NAME_LABEL} 
                id="name"
                name="name"
                value={formData.name}
                readOnly 
                disabled 
                hint="Имя страницы используется как ID и не может быть изменено."
              />
           </div>
           <div className="sm:col-span-1">
             <Input label={text.PAGE_CREATE_WIDTH_LABEL} id="width" name="width" type="number" value={formData.width} onChange={handleChange} required min="1" />
           </div>
           <div className="sm:col-span-1">
             <Input label={text.PAGE_CREATE_HEIGHT_LABEL} id="height" name="height" type="number" value={formData.height} onChange={handleChange} required min="1" />
           </div>
           <div className="sm:col-span-1">
             <Select label={text.PAGE_CREATE_UNITS_LABEL} id="units" name="units" value={formData.units} onChange={handleChange} options={pageUnitsOptions} required />
           </div>
           <div className="sm:col-span-2">
             <Input label={text.PAGE_CREATE_BLEEDS_LABEL} id="bleeds" name="bleeds" type="number" value={formData.bleeds} onChange={handleChange} min="0" hint="В мм или px" />
           </div>
         </div>
       </Card>

       {/* HTML Редактор */} 
       <Card title={PAGE_EDIT_SECTION_HTML}>
         <CodeEditor value={formData.html} onChange={handleHtmlChange} language="html" height="500px" />
       </Card>

       {/* Поля */} 
       <Card 
         title={PAGE_EDIT_SECTION_FIELDS}
         titleRight={
             <Button type="button" variant="outline" size="sm" onClick={handleAddField} icon={<PlusCircle size={16}/>}>
                 {PAGE_EDIT_ADD_FIELD_BUTTON}
             </Button>
         }
       >
         {/* ... (код рендеринга полей как в PageCreate) ... */} 
          {fields.length === 0 ? (
             <p className="text-center text-gray-500 py-4">{text.HOME_NO_FIELDS_IN_TEMPLATE}</p>
          ) : (
             <div className="space-y-4">
               {fields.map((field, index) => (
                 <div key={index} className="grid grid-cols-1 gap-4 sm:grid-cols-8 items-end border-b border-gray-100 pb-4">
                   <div className="sm:col-span-3">
                     <Input label={text.PAGE_CREATE_FIELD_NAME_LABEL} value={field.name} onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })} placeholder={text.PAGE_CREATE_FIELD_NAME_PLACEHOLDER} required />
                   </div>
                   <div className="sm:col-span-3">
                     <Input label={text.PAGE_CREATE_FIELD_LABEL_LABEL} value={field.label} onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })} placeholder={text.PAGE_CREATE_FIELD_LABEL_PLACEHOLDER} required />
                   </div>
                   <div className="sm:col-span-1 flex items-center pt-5">
                     <Checkbox id={`required-${index}`} checked={field.required} onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })} label={PAGE_EDIT_FIELD_REQUIRED_LABEL} />
                   </div>
                   <div className="sm:col-span-1 flex justify-end pt-5">
                     <Button type="button" variant="ghost" size="sm" icon={<Trash2 className="text-red-600" />} onClick={() => handleDeleteField(index)} title={PAGE_EDIT_DELETE_FIELD_BUTTON} />
                   </div>
                 </div>
               ))}
             </div>
          )}
       </Card>
       
       {/* Ассеты */} 
       <Card
          title={PAGE_EDIT_SECTION_ASSETS}
          titleRight={
             <FileUploader onFileUpload={handleFileUpload} buttonText={PAGE_EDIT_UPLOAD_ASSET_BUTTON} />
          }
       >
           {page.assets?.length === 0 ? (
              <p className="text-center text-gray-500 py-4">Нет загруженных ассетов.</p>
           ) : (
              <ul className="divide-y divide-gray-100 -mx-6"> {/* Убираем отступы Card */} 
                 {page.assets?.map((asset) => (
                   <li key={asset.id} className="px-6 py-3 flex items-center justify-between hover:bg-gray-50">
                       <div className="flex items-center space-x-3">
                          <ImageIcon className="text-gray-400" size={20}/>
                          <div>
                             <span className="text-sm font-medium text-gray-900">{asset.name}</span>
                             {/* Показываем URL или путь для использования в HTML */} 
                             <span 
                                className="ml-2 text-xs text-gray-500 cursor-pointer hover:text-blue-600"
                                title="Копировать путь"
                                onClick={() => copyAssetPath(asset.url)} // Предполагаем, что URL это и есть путь
                             >
                                {asset.url}
                             </span>
                          </div>
                       </div>
                       <div className="flex items-center space-x-2">
                           <a href={asset.url} target="_blank" rel="noopener noreferrer" title="Открыть в новой вкладке">
                               <Button variant="ghost" size="sm" icon={<ExternalLink size={16}/>} />
                           </a>
                           <Button 
                             variant="ghost" 
                             size="sm" 
                             icon={<Copy size={16} />} 
                             onClick={() => copyAssetPath(asset.url)}
                             title={PAGE_EDIT_COPY_ASSET_PATH_BUTTON}
                           />
                           <Button 
                             variant="ghost" 
                             size="sm" 
                             icon={<Trash2 className="text-red-600" size={16}/>} 
                             onClick={() => openDeleteAssetConfirm(asset)}
                             title={PAGE_EDIT_DELETE_ASSET_BUTTON}
                           />
                       </div>
                   </li>
                 ))}
              </ul>
           )}
       </Card>

       {/* Нижние кнопки сохранения */} 
       <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Link to={`/admin/templates/${templateId}`}>
                <Button type="button" variant="outline" disabled={saving}>
                    {PAGE_EDIT_CANCEL_BUTTON}
                </Button>
             </Link>
             <Button type="submit" isLoading={saving} icon={<Save size={16} />}>
               {saving ? PAGE_EDIT_SAVING_BUTTON : PAGE_EDIT_SAVE_BUTTON}
             </Button>
       </div>
       
       {/* Модальное окно подтверждения удаления ассета */} 
        <Modal 
         isOpen={showDeleteAssetConfirm}
         onClose={closeDeleteAssetConfirm}
         title={PAGE_EDIT_CONFIRM_DELETE_ASSET_TITLE}
         size="md"
       >
         <div className="space-y-4">
            <div className="flex items-start space-x-3">
                 <AlertTriangle className="h-10 w-10 text-red-500 flex-shrink-0"/>
                 <p className="text-sm text-gray-600">
                     {PAGE_EDIT_CONFIRM_DELETE_ASSET_MSG(assetToDelete?.name || '')}
                 </p>
            </div>
            {deleteAssetError && (
               <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{deleteAssetError}</p>
            )}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                 <Button variant="outline" onClick={closeDeleteAssetConfirm} disabled={isDeletingAsset}>
                     {text.CANCEL_BUTTON}
                 </Button>
                 <Button variant="danger" onClick={handleDeleteAsset} isLoading={isDeletingAsset}>
                     {PAGE_EDIT_DELETE_ASSET_BUTTON}
                 </Button>
            </div>
         </div>
       </Modal>

    </form>
  );
};

export default PageEdit;