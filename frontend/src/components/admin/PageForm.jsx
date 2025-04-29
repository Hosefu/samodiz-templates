import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Alert, Divider, Row, Col, Space, Typography } from 'antd';
import { toast } from 'react-hot-toast';
import { 
  Save, ChevronLeft, PlusCircle, Trash2, Loader2, AlertTriangle, 
  Upload as UploadIcon, ExternalLink, Image as ImageIcon
} from 'lucide-react';
import CodeEditor from '../admin/CodeEditor';
import { Button, Input, Select, Checkbox, Card } from '../ui/UIComponents';
import Modal from '../ui/Modal';
import * as text from '../../constants/ux-writing';
import AssetManager from './AssetManager';
import { uploadAsset, deleteAsset } from '../../api/assetService';

const PageForm = ({ 
  mode = 'create', 
  templateId,
  templateName = '',
  pageId = null,
  initialData = null,
  onSubmit,
  isSubmitting = false,
  error = null
}) => {
  // Form states
  const [formData, setFormData] = useState({
    name: '',
    width: 210,
    height: 297,
    units: 'mm',
    bleeds: 3,
    html: ''
  });
  const [fields, setFields] = useState([]);
  const [assets, setAssets] = useState([]);
  const [formError, setFormError] = useState(null);
  
  // Asset deletion states
  const [showDeleteAssetConfirm, setShowDeleteAssetConfirm] = useState(false);
  const [assetToDelete, setAssetToDelete] = useState(null);
  const [isDeletingAsset, setIsDeletingAsset] = useState(false);
  const [deleteAssetError, setDeleteAssetError] = useState(null);
  
  const navigate = useNavigate();

  // Initialize form with data
  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        width: initialData.width || 210,
        height: initialData.height || 297,
        units: initialData.units || 'mm',
        bleeds: initialData.bleeds || 3,
        html: initialData.html || DEFAULT_HTML_TEMPLATE
      });
      setFields(initialData.fields || []);
      setAssets(initialData.assets || []);
    } else {
      // Default values for new page
      setFormData({
        name: '',
        width: 210,
        height: 297,
        units: 'mm',
        bleeds: 3,
        html: DEFAULT_HTML_TEMPLATE
      });
      setFields([
        { name: 'title', label: 'Заголовок документа', required: true },
        { name: 'name', label: 'Имя получателя', required: true }
      ]);
      setAssets([]);
    }
  }, [initialData]);

  // Form change handlers
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
    setFormError(null);
  };

  const handleSelectChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    setFormError(null);
  };

  const handleHtmlChange = (newValue) => {
    setFormData(prev => ({ ...prev, html: newValue }));
    setFormError(null);
  };

  // Field handlers
  const handleAddField = () => {
    setFields([...fields, { name: '', label: '', required: false }]);
  };

  const handleFieldChange = (index, field) => {
    const newFields = [...fields];
    newFields[index] = field;
    setFields(newFields);
  };

  const handleDeleteField = (index) => {
    setFields(fields.filter((_, i) => i !== index));
  };

  // Asset handlers
  const handleFileUpload = async (file) => {
    try {
      if (!file) {
        toast.error('Файл не выбран');
        return;
      }
      
      const asset = await uploadAsset(templateId, pageId, file);
      setAssets(prev => [...prev, asset]);
      toast.success(`Ассет "${file.name}" загружен`);
    } catch (err) {
      console.error('Failed to upload file:', err);
      toast.error(err.message || 'Ошибка загрузки файла');
    }
  };
  
  const handleAssetsChange = (updatedAssets) => {
    setAssets(updatedAssets);
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
    
    try {
      setIsDeletingAsset(true);
      await deleteAsset(templateId, pageId, assetToDelete.id);
      setAssets(assets.filter(asset => asset.id !== assetToDelete.id));
      toast.success('Ассет удален');
      closeDeleteAssetConfirm();
    } catch (err) {
      console.error('Failed to delete asset:', err);
      setDeleteAssetError(err.message || 'Ошибка удаления ассета');
    } finally {
      setIsDeletingAsset(false);
    }
  };

  // Form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.name.trim()) {
      setFormError('Имя страницы обязательно');
      return;
    }
    
    // Validate fields
    const invalidFields = fields.filter(field => !field.name.trim() || !field.label.trim());
    if (invalidFields.length > 0) {
      setFormError('Все поля должны иметь имя и метку');
      return;
    }
    
    // Collect form data
    const pageData = {
      ...formData,
      fields: fields,
      assets: assets
    };
    
    // Call submit handler
    onSubmit(pageData);
  };

  // Constants and options
  const pageUnitsOptions = [
    { value: 'mm', label: 'Миллиметры (mm)' },
    { value: 'px', label: 'Пиксели (px)' },
  ];

  // Titles based on mode
  const pageTitle = mode === 'create' ? 'Создание новой страницы' : `Редактирование страницы: ${formData.name}`;
  const formTitle = mode === 'create' ? 'Новая страница шаблона' : `Редактирование страницы: ${formData.name}`;

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Breadcrumbs and buttons */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to={`/admin/templates/${templateId}`} className="text-gray-500 hover:text-gray-700" title={`К шаблону "${templateName}"`}>
            <ChevronLeft size={24}/>
          </Link>
          <h1 className="text-2xl font-semibold text-gray-800">{pageTitle}</h1>
        </div>
        <div className="flex space-x-3">
          <Link to={`/admin/templates/${templateId}`}>
            <Button type="button" variant="outline" disabled={isSubmitting}>
              Отмена
            </Button>
          </Link>
          <Button type="submit" isLoading={isSubmitting} icon={<Save size={16} />}>
            {isSubmitting ? 'Сохранение...' : 'Сохранить страницу'}
          </Button>
        </div>
      </div>

      {/* Form errors */}
      {(error || formError) && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md text-sm" role="alert">
          {error || formError}
        </div>
      )}
       
      {/* Page details */}
      <Card title="Детали страницы">
        <div className="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <Input
              label="Название страницы (ID)"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              readOnly={mode === 'edit'}
              disabled={mode === 'edit'}
              hint={mode === 'edit' ? "Имя страницы используется как ID и не может быть изменено." : undefined}
              required
            />
          </div>
          <div className="sm:col-span-1">
            <Input 
              label="Ширина" 
              id="width" 
              name="width" 
              type="number" 
              value={formData.width} 
              onChange={handleChange} 
              required 
              min="1" 
            />
          </div>
          <div className="sm:col-span-1">
            <Input 
              label="Высота" 
              id="height" 
              name="height" 
              type="number" 
              value={formData.height} 
              onChange={handleChange} 
              required 
              min="1" 
            />
          </div>
          <div className="sm:col-span-1">
            <Select 
              label="Единицы измерения" 
              id="units" 
              name="units" 
              value={formData.units} 
              onChange={(value) => handleSelectChange('units', value)} 
              options={pageUnitsOptions} 
              required 
            />
          </div>
          <div className="sm:col-span-2">
            <Input 
              label="Вылеты" 
              id="bleeds" 
              name="bleeds" 
              type="number" 
              value={formData.bleeds} 
              onChange={handleChange} 
              min="0" 
              hint="В мм или px" 
            />
          </div>
        </div>
      </Card>

      {/* HTML Editor */}
      <Card title="HTML разметка страницы">
        <CodeEditor 
          value={formData.html} 
          onChange={handleHtmlChange} 
          language="html" 
          height="500px" 
        />
      </Card>

      {/* Fields */}
      <Card 
        title="Поля шаблона (переменные)"
        titleRight={
          <Button 
            type="button" 
            variant="outline" 
            size="sm" 
            onClick={handleAddField} 
            icon={<PlusCircle size={16}/>}
          >
            Добавить поле
          </Button>
        }
      >
        {fields.length === 0 ? (
          <p className="text-center text-gray-500 py-4">
            Поля еще не добавлены. Нажмите "Добавить поле", чтобы создать поля формы для вашего шаблона.
          </p>
        ) : (
          <div className="space-y-4">
            {fields.map((field, index) => (
              <div key={index} className="grid grid-cols-1 gap-4 sm:grid-cols-8 items-end border-b border-gray-100 pb-4">
                <div className="sm:col-span-3">
                  <Input 
                    label="Название поля (переменной)" 
                    value={field.name} 
                    onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })} 
                    placeholder="например, client_name" 
                    required 
                  />
                </div>
                <div className="sm:col-span-3">
                  <Input 
                    label="Метка поля (для формы)" 
                    value={field.label} 
                    onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })} 
                    placeholder="например, Имя клиента" 
                    required 
                  />
                </div>
                <div className="sm:col-span-1 flex items-center pt-5">
                  <Checkbox 
                    id={`required-${index}`} 
                    checked={field.required} 
                    onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })} 
                    label="Обяз." 
                  />
                </div>
                <div className="sm:col-span-1 flex justify-end pt-5">
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    icon={<Trash2 className="text-red-600" />} 
                    onClick={() => handleDeleteField(index)} 
                    title="Удалить поле" 
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
       
      {/* Assets */}
      <Card title="Ассеты (изображения, шрифты)">
        {mode === 'create' ? (
          <p className="text-center text-gray-500 py-4">
            Для загрузки ассетов сначала сохраните страницу.
          </p>
        ) : (
          <AssetManager 
            templateId={templateId}
            pageId={pageId}
            assets={assets}
            onAssetsChange={handleAssetsChange}
          />
        )}
      </Card>
      
      {/* Delete asset confirmation modal */}
      {showDeleteAssetConfirm && (
        <Modal
          title="Подтвердите удаление"
          isOpen={showDeleteAssetConfirm}
          onClose={closeDeleteAssetConfirm}
          footer={
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={closeDeleteAssetConfirm}
                disabled={isDeletingAsset}
              >
                Отмена
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteAsset}
                isLoading={isDeletingAsset}
              >
                {isDeletingAsset ? 'Удаление...' : 'Удалить'}
              </Button>
            </div>
          }
        >
          <p>
            Вы уверены, что хотите удалить ассет "{assetToDelete?.name || 'Неизвестный файл'}"?
            Использующие его шаблоны могут сломаться.
          </p>
          {deleteAssetError && (
            <Alert
              type="error"
              message={deleteAssetError}
              className="mt-4"
            />
          )}
        </Modal>
      )}

      {/* Bottom save buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <Link to={`/admin/templates/${templateId}`}>
          <Button type="button" variant="outline" disabled={isSubmitting}>
            Отмена
          </Button>
        </Link>
        <Button type="submit" isLoading={isSubmitting} icon={<Save size={16} />}>
          {isSubmitting ? 'Сохранение...' : 'Сохранить страницу'}
        </Button>
      </div>
    </form>
  );
};

export default PageForm;

// Default HTML template
const DEFAULT_HTML_TEMPLATE = `<!DOCTYPE html>
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