import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTemplate } from '../../api/templateService';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { Form, Select, Input, Button, Card, Alert, Space } from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';

const TemplateCreate = () => {
  const navigate = useNavigate();
  const { refreshTemplates } = useTemplates();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [form] = Form.useForm();

  // Список типов шаблонов
  const templateTypeOptions = [
    { value: 'pdf', label: 'PDF' },
    { value: 'png', label: 'PNG' },
    { value: 'svg', label: 'SVG' },
    { value: 'docx', label: 'DOCX' },
    { value: 'xlsx', label: 'XLSX' },
    { value: 'html', label: 'HTML' }
  ];

  const handleSubmit = async (values) => {
    setLoading(true);
    setError(null);
    
    try {
      const newTemplate = await createTemplate(values);
      refreshTemplates();
      navigate(`/admin/templates/${newTemplate.id}`);
    } catch (err) {
      console.error('Failed to create template:', err);
      setError(text.TEMPLATE_CREATE_ERROR(err.message || text.UNKNOWN_ERROR_MSG));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-medium">{text.TEMPLATE_CREATE_TITLE}</h3>
        <p className="text-gray-500">{text.TEMPLATE_CREATE_DESCRIPTION}</p>
      </div>

      {error && (
        <div style={{ marginBottom: 16 }}>
          <Alert message="Ошибка" description={error} type="error" showIcon />
        </div>
      )}

      <Card>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            name: '',
            version: '1.0',
            type: 'pdf'
          }}
          onFinish={handleSubmit}
        >
          <Form.Item 
            name="name" 
            label={text.TEMPLATE_CREATE_NAME_LABEL}
            rules={[
              { required: true, message: text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_NAME_LABEL) }
            ]}
          >
            <Input placeholder={text.TEMPLATE_CREATE_NAME_PLACEHOLDER} />
          </Form.Item>

          <Form.Item 
            name="version" 
            label={text.TEMPLATE_CREATE_VERSION_LABEL}
            rules={[
              { required: true, message: text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_VERSION_LABEL) }
            ]}
          >
            <Input placeholder={text.TEMPLATE_CREATE_VERSION_PLACEHOLDER} />
          </Form.Item>

          <Form.Item 
            name="type" 
            label={text.TEMPLATE_CREATE_TYPE_LABEL}
            rules={[
              { required: true, message: text.REQUIRED_ERROR_MSG(text.TEMPLATE_CREATE_TYPE_LABEL) }
            ]}
          >
            <Select
              placeholder={text.TEMPLATE_CREATE_SELECT_TYPE}
              options={templateTypeOptions}
            />
          </Form.Item>

          <Form.Item>
            <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                onClick={() => navigate('/admin/templates')}
                icon={<ArrowLeftOutlined />}
              >
                {text.CANCEL_BUTTON}
              </Button>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                icon={<SaveOutlined />}
              >
                {loading ? text.TEMPLATE_CREATE_SUBMITTING_BUTTON : text.TEMPLATE_CREATE_SUBMIT_BUTTON}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default TemplateCreate; 