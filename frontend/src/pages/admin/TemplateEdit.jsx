import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { fetchTemplateById, updateTemplate } from '../../api/templateService';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { 
  Button, Input, Card, Select, Form, message
} from '../../components/ui/AntComponents';
import { 
  ArrowLeftOutlined, SaveOutlined, FileAddOutlined, 
  EditOutlined, DeleteOutlined 
} from '@ant-design/icons';
import { Alert, List, Typography, Space, Spin } from 'antd';
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

  // Список типов шаблонов
  const templateTypeOptions = [
    { value: 'pdf', label: 'PDF' },
    { value: 'png', label: 'PNG' },
    { value: 'svg', label: 'SVG' },
    { value: 'docx', label: 'DOCX' },
    { value: 'xlsx', label: 'XLSX' },
    { value: 'html', label: 'HTML' }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Spin size="large" />
        <span className="ml-2 text-gray-600">{TPL_EDIT_LOADING}</span>
      </div>
    );
  }

  // Показываем ошибку загрузки, если шаблон не загружен
  if (error && !template) {
    return (
      <div className="text-center py-10">
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          showIcon
        />
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
    <div>
      {/* Заголовок и кнопки действий */}
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Space>
          <Link to="/admin/templates">
            <Button icon={<ArrowLeftOutlined />} />
          </Link>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {TPL_EDIT_TITLE}: {template.name}
          </Typography.Title>
        </Space>
      </Space>

      {/* Форма */}
      <Card title={TPL_EDIT_SECTION_DETAILS}>
        <Form
          layout="vertical"
          initialValues={formData}
          onFinish={handleSubmit}
        >
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            label={text.TEMPLATE_CREATE_NAME_LABEL}
            required
          />
          
          <Input
            name="version"
            value={formData.version}
            onChange={handleChange}
            label={text.TEMPLATE_CREATE_VERSION_LABEL}
            required
          />
          
          <Select
            name="type"
            value={formData.type}
            onChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
            label={text.TEMPLATE_CREATE_TYPE_LABEL}
            options={templateTypeOptions}
            required
          />
          
          {/* Кнопки действий */}
          <Form.Item>
            <Space style={{ justifyContent: 'flex-end', width: '100%' }}>
              <Button 
                onClick={() => setFormData({ name: template.name, version: template.version, type: template.type })}
                disabled={saving}
              >
                {TPL_EDIT_CANCEL_BUTTON}
              </Button>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={saving}
                icon={<SaveOutlined />}
              >
                {saving ? TPL_EDIT_SAVING_BUTTON : TPL_EDIT_SAVE_BUTTON}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* Список страниц */}
      <Card 
        title={TPL_EDIT_SECTION_PAGES}
        extra={
          <Button
            type="primary"
            icon={<FileAddOutlined />}
            onClick={() => navigate(`/admin/templates/${id}/pages/new`)}
          >
            {TPL_EDIT_ADD_PAGE_BUTTON}
          </Button>
        }
      >
        {template.pages && template.pages.length > 0 ? (
          <List
            dataSource={template.pages}
            renderItem={page => (
              <List.Item
                actions={[
                  <Button
                    key="edit"
                    icon={<EditOutlined />}
                    onClick={() => navigate(`/admin/templates/${id}/pages/${page.name}`)}
                  >
                    {TPL_EDIT_EDIT_PAGE_BUTTON}
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={page.name}
                  description={TPL_EDIT_PAGE_DETAILS(
                    page.width,
                    page.height,
                    page.units,
                    page.fields?.length || 0,
                    page.assets?.length || 0
                  )}
                />
              </List.Item>
            )}
          />
        ) : (
          <div className="text-center py-4 text-gray-500">
            {TPL_EDIT_NO_PAGES}
          </div>
        )}
      </Card>
    </div>
  );
};

export default TemplateEdit; 