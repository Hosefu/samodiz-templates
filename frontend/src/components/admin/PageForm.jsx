import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Space, Alert, Row, Col, Typography } from 'antd';
import { toast } from 'react-hot-toast';
import { ChevronLeft, Save, PlusCircle, Trash2 } from 'lucide-react';
import CodeEditor from './CodeEditor';
import { Button, Input, Select, Checkbox, Card } from '../ui/UIComponents';
import AssetManager from './AssetManager';

// Общие константы для страниц создания/редактирования
const PAGE_FORM_FIELD_NAME_LABEL = "Название поля (переменной)";
const PAGE_FORM_FIELD_LABEL_LABEL = "Метка поля (для формы)";
const PAGE_FORM_FIELD_REQUIRED_LABEL = "Обязательное";
const PAGE_FORM_ADD_FIELD_BUTTON = "Добавить поле";
const PAGE_FORM_DELETE_FIELD_BUTTON = "Удалить поле";
const PAGE_FORM_UNITS_OPTIONS = [
  { value: 'mm', label: 'Миллиметры (mm)' },
  { value: 'px', label: 'Пиксели (px)' },
];

const PageForm = ({ 
  mode = 'create', 
  templateId, 
  initialData = null, 
  pageId = null, 
  onSubmit,
  isSubmitting,
  error
}) => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [fields, setFields] = useState([]);
  const [assets, setAssets] = useState([]);
  
  // Задание значений по умолчанию в зависимости от режима
  useEffect(() => {
    if (mode === 'edit' && initialData) {
      form.setFieldsValue({
        name: initialData.name,
        width: initialData.width,
        height: initialData.height,
        units: initialData.units,
        bleeds: initialData.bleeds,
        html: initialData.html
      });
      setFields(initialData.fields || []);
      setAssets(initialData.assets || []);
    } else {
      // Значения по умолчанию для создания
      form.setFieldsValue({
        name: '',
        width: 210,
        height: 297,
        units: 'mm',
        bleeds: 3,
        html: defaultHtml
      });
      setFields([
        { name: 'title', label: 'Заголовок документа', required: true },
        { name: 'name', label: 'Имя получателя', required: true }
      ]);
      setAssets([]);
    }
  }, [mode, initialData, form]);

  const handleHtmlChange = (newValue) => {
    form.setFieldsValue({ html: newValue });
  };

  const handleSubmit = (values) => {
    const pageData = {
      ...values,
      fields,
      assets
    };
    
    onSubmit(pageData);
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
    setFields(fields.filter((_, i) => i !== index));
  };

  const handleAssetsChange = (newAssets) => {
    setAssets(newAssets);
  };

  // Определяем заголовок и текст кнопок в зависимости от режима
  const title = mode === 'create' ? 'Создание новой страницы' : 'Редактирование страницы';
  const submitButtonText = mode === 'create' ? 'Создать страницу' : 'Сохранить страницу';
  
  return (
    <Form 
      form={form}
      onFinish={handleSubmit}
      layout="vertical"
    >
      {/* Заголовок и кнопки действий */}
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Space>
          <Link to={`/admin/templates/${templateId}`}>
            <Button icon={<ChevronLeft size={16} />} variant="ghost" />
          </Link>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {title}
            {mode === 'edit' && pageId && <span className="font-normal ml-2">{pageId}</span>}
          </Typography.Title>
        </Space>
        <Space>
          <Link to={`/admin/templates/${templateId}`}>
            <Button variant="outline">Отмена</Button>
          </Link>
          <Button 
            type="submit"
            isLoading={isSubmitting}
            icon={<Save size={16} />}
          >
            {isSubmitting ? 'Сохранение...' : submitButtonText}
          </Button>
        </Space>
      </Space>

      {/* Ошибка */}
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      {/* Детали страницы */}
      <Card title="Детали страницы" className="mb-6">
        <Row gutter={16}>
          <Col span={mode === 'edit' ? 8 : 6}>
            <Form.Item
              name="name"
              label="Название страницы (ID)"
              rules={[{ required: true, message: "Название страницы обязательно" }]}
              tooltip={mode === 'edit' ? "Имя страницы используется как ID и не может быть изменено." : null}
            >
              <Input disabled={mode === 'edit'} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="width"
              label="Ширина"
              rules={[{ required: true, message: "Ширина обязательна" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="height"
              label="Высота"
              rules={[{ required: true, message: "Высота обязательна" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={mode === 'edit' ? 4 : 5}>
            <Form.Item
              name="units"
              label="Единицы изм."
              rules={[{ required: true, message: "Выберите единицы измерения" }]}
            >
              <Select options={PAGE_FORM_UNITS_OPTIONS} />
            </Form.Item>
          </Col>
          <Col span={mode === 'edit' ? 4 : 5}>
            <Form.Item
              name="bleeds"
              label="Вылеты (bleeds)"
              tooltip="Отступы под обрез (в выбранных единицах)"
            >
              <Input type="number" min={0} />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* HTML редактор */}
      <Card title="HTML разметка страницы" className="mb-6">
        <Form.Item name="html">
          <CodeEditor 
            language="html" 
            height="400px"
            onChange={handleHtmlChange}
          />
        </Form.Item>
      </Card>

      {/* Поля шаблона */}
      <Card 
        title="Поля шаблона (переменные)" 
        extra={
          <Button 
            variant="primary" 
            icon={<PlusCircle size={16} />} 
            onClick={handleAddField}
          >
            {PAGE_FORM_ADD_FIELD_BUTTON}
          </Button>
        }
        className="mb-6"
      >
        {fields.length === 0 ? (
          <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: '24px 0' }}>
            Поля еще не добавлены
          </Typography.Text>
        ) : (
          <div className="space-y-4">
            {fields.map((field, index) => (
              <div key={index} className="grid grid-cols-8 gap-4 items-end border-b border-gray-600 pb-4">
                <div className="col-span-3">
                  <Form.Item
                    label={PAGE_FORM_FIELD_NAME_LABEL}
                    required
                  >
                    <Input
                      placeholder="например, client_name"
                      value={field.name}
                      onChange={(e) => handleFieldChange(index, { ...field, name: e.target.value })}
                    />
                  </Form.Item>
                </div>
                <div className="col-span-3">
                  <Form.Item
                    label={PAGE_FORM_FIELD_LABEL_LABEL}
                    required
                  >
                    <Input
                      placeholder="Например, Имя клиента"
                      value={field.label}
                      onChange={(e) => handleFieldChange(index, { ...field, label: e.target.value })}
                    />
                  </Form.Item>
                </div>
                <div className="col-span-1 pt-5">
                  <Checkbox
                    checked={field.required}
                    onChange={(e) => handleFieldChange(index, { ...field, required: e.target.checked })}
                    label={PAGE_FORM_FIELD_REQUIRED_LABEL}
                  />
                </div>
                <div className="col-span-1 flex justify-end pt-5">
                  <Button
                    variant="ghost"
                    icon={<Trash2 className="text-red-500" size={16} />}
                    onClick={() => handleDeleteField(index)}
                    title={PAGE_FORM_DELETE_FIELD_BUTTON}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Управление файлами */}
      <Card title="Управление файлами" className="mb-6">
        <AssetManager
          templateId={templateId}
          pageId={pageId}
          assets={assets}
          onAssetsChange={handleAssetsChange}
        />
      </Card>

      {/* Нижние кнопки */}
      <div className="flex justify-end space-x-3">
        <Link to={`/admin/templates/${templateId}`}>
          <Button variant="outline" disabled={isSubmitting}>
            Отмена
          </Button>
        </Link>
        <Button 
          type="submit"
          isLoading={isSubmitting}
          icon={<Save size={16} />}
        >
          {isSubmitting ? 'Сохранение...' : submitButtonText}
        </Button>
      </div>
    </Form>
  );
};

export default PageForm; 