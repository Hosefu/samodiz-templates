import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { createPage } from '../../api/pageService';
import * as text from '../../constants/ux-writing';
import { 
  Button, Card, Form, Input, Select, Checkbox,
  message, Icons
} from '../../components/ui/AntComponents';
import { 
  ArrowLeftOutlined, DeleteOutlined, PlusOutlined 
} from '@ant-design/icons';
import { Space, Alert, Divider, Row, Col } from 'antd';
import CodeEditor from '../../components/admin/CodeEditor';

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
      message.success(`Страница "${newPage.name}" успешно создана!`);
      // Переходим на страницу редактирования созданного шаблона
      navigate(`/admin/templates/${templateId}`); 
    } catch (err) {
      console.error('Failed to create page:', err);
      const errorMsg = PAGE_CREATE_ERROR(err.response?.data?.detail || err.message || text.UNKNOWN_ERROR_MSG);
      setError(errorMsg);
      message.error(errorMsg);
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
    <Form onFinish={handleSubmit} layout="vertical" initialValues={formData}>
      {/* Header с кнопками */}
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Space>
          <Link to={`/admin/templates/${templateId}`}>
            <Button icon={<ArrowLeftOutlined />} />
          </Link>
          <div>
            <Typography.Title level={4} style={{ margin: 0 }}>
              {PAGE_CREATE_TITLE}
            </Typography.Title>
            <Typography.Text type="secondary">
              {PAGE_CREATE_DESCRIPTION(templateId)}
            </Typography.Text>
          </div>
        </Space>
        <Space>
          <Link to={`/admin/templates/${templateId}`}>
            <Button>{PAGE_CREATE_CANCEL_BUTTON}</Button>
          </Link>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            icon={<SaveOutlined />}
          >
            {loading ? PAGE_CREATE_SUBMITTING_BUTTON : PAGE_CREATE_SUBMIT_BUTTON}
          </Button>
        </Space>
      </Space>

      {/* Ошибка */}
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      {/* Детали страницы */}
      <Card title={PAGE_CREATE_SECTION_DETAILS}>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="name"
              label={PAGE_CREATE_NAME_LABEL}
              rules={[{ required: true, message: "Название страницы обязательно" }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="width"
              label={PAGE_CREATE_WIDTH_LABEL}
              rules={[{ required: true, message: "Ширина обязательна" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="height"
              label={PAGE_CREATE_HEIGHT_LABEL}
              rules={[{ required: true, message: "Высота обязательна" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="units"
              label={PAGE_CREATE_UNITS_LABEL}
              rules={[{ required: true, message: "Выберите единицы измерения" }]}
            >
              <Select options={PAGE_CREATE_UNITS_OPTIONS} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="bleeds"
              label={PAGE_CREATE_BLEEDS_LABEL}
              tooltip="Отступы под обрез (в выбранных единицах)"
            >
              <Input type="number" min={0} />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* HTML Редактор */}
      <Card title={PAGE_CREATE_SECTION_HTML} style={{ marginTop: 16 }}>
        <Form.Item name="html">
          <CodeEditor 
            language="html" 
            height="400px"
            value={formData.html}
            onChange={(value) => setFormData(prev => ({ ...prev, html: value }))}
          />
        </Form.Item>
      </Card>

      {/* Поля шаблона */}
      <Card 
        title={PAGE_CREATE_SECTION_FIELDS} 
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={handleAddField}
          >
            {PAGE_CREATE_ADD_FIELD_BUTTON}
          </Button>
        }
        style={{ marginTop: 16 }}
      >
        {fields.length === 0 ? (
          <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: '24px 0' }}>
            {text.HOME_NO_FIELDS_IN_TEMPLATE}
          </Typography.Text>
        ) : (
          <div>
            {fields.map((field, index) => (
              <Row key={index} gutter={16} align="middle" style={{ marginBottom: 16 }}>
                <Col span={8}>
                  <Form.Item
                    label={PAGE_CREATE_FIELD_NAME_LABEL}
                    required
                  >
                    <Input
                      placeholder={PAGE_CREATE_FIELD_NAME_PLACEHOLDER}
                      value={field.name}
                      onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label={PAGE_CREATE_FIELD_LABEL_LABEL}
                    required
                  >
                    <Input
                      placeholder={PAGE_CREATE_FIELD_LABEL_PLACEHOLDER}
                      value={field.label}
                      onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })}
                    />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item label=" " colon={false}>
                    <Checkbox
                      checked={field.required}
                      onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })}
                    >
                      {PAGE_CREATE_FIELD_REQUIRED_LABEL}
                    </Checkbox>
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDeleteField(index)}
                    title={PAGE_CREATE_DELETE_FIELD_BUTTON}
                  />
                </Col>
              </Row>
            ))}
          </div>
        )}
      </Card>
    </Form>
  );
};

export default PageCreate; 