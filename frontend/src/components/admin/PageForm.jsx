import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Form, Row, Col, Space, Typography, Alert } from 'antd';
import { SaveOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { createPage, updatePage } from '../../redux/slices/pageSlice';
import CodeEditor from './CodeEditor';
import AssetManager from './AssetManager';
import { Button, Input, Select, Checkbox, Card } from '../ui/UIComponents';

const PageForm = ({ 
  mode = 'create', 
  templateId, 
  pageId = null, 
  initialData = null 
}) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [fields, setFields] = useState([]);
  const [html, setHtml] = useState('');
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const { currentTemplate } = useSelector(state => state.templates);
  
  // Initialize form with data
  useEffect(() => {
    if (mode === 'edit' && initialData) {
      form.setFieldsValue({
        name: initialData.name,
        width: initialData.width,
        height: initialData.height,
        units: initialData.units,
        bleeds: initialData.bleeds
      });
      setHtml(initialData.html || '');
      setFields(initialData.fields || []);
      setAssets(initialData.assets || []);
    } else {
      // Default values for new page
      form.setFieldsValue({
        width: 210,
        height: 297,
        units: 'mm',
        bleeds: 3
      });
      setHtml(DEFAULT_HTML_TEMPLATE);
      setFields([
        { name: 'title', label: 'Document Title', required: true },
        { name: 'name', label: 'Recipient Name', required: true }
      ]);
    }
  }, [form, initialData, mode]);
  
  const handleHtmlChange = (value) => {
    setHtml(value);
  };
  
  const handleSubmit = async (values) => {
    try {
      setLoading(true);
      setError(null);
      
      const pageData = {
        ...values,
        html,
        fields,
        assets
      };
      
      if (mode === 'create') {
        await dispatch(createPage({ templateId, pageData })).unwrap();
        navigate(`/admin/templates/${templateId}`);
      } else {
        await dispatch(updatePage({ templateId, pageId, pageData })).unwrap();
        navigate(`/admin/templates/${templateId}`);
      }
    } catch (err) {
      setError(err.message || 'Failed to save page');
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <Form 
      layout="vertical" 
      form={form} 
      onFinish={handleSubmit}
      initialValues={{
        name: '',
        width: 210,
        height: 297,
        units: 'mm',
        bleeds: 3
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <Typography.Title level={4}>
          {mode === 'create' ? 'Create New Page' : `Edit Page: ${pageId}`}
        </Typography.Title>
        <Space>
          <Button onClick={() => navigate(`/admin/templates/${templateId}`)}>
            Cancel
          </Button>
          <Button 
            type="primary" 
            htmlType="submit" 
            icon={<SaveOutlined />} 
            loading={loading}
          >
            {loading ? 'Saving...' : 'Save Page'}
          </Button>
        </Space>
      </div>

      {error && <Alert message={error} type="error" className="mb-4" />}

      {/* Page Details */}
      <Card title="Page Details" className="mb-4">
        <Row gutter={16}>
          <Col span={mode === 'edit' ? 8 : 6}>
            <Form.Item
              name="name"
              label="Page Name (ID)"
              rules={[{ required: true, message: "Page name is required" }]}
              tooltip={mode === 'edit' ? "Name cannot be changed as it is used as an ID" : null}
            >
              <Input disabled={mode === 'edit'} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="width"
              label="Width"
              rules={[{ required: true, message: "Width is required" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={4}>
            <Form.Item
              name="height"
              label="Height"
              rules={[{ required: true, message: "Height is required" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
          </Col>
          <Col span={5}>
            <Form.Item
              name="units"
              label="Units"
              rules={[{ required: true, message: "Units are required" }]}
            >
              <Select options={[
                { value: 'mm', label: 'Millimeters (mm)' },
                { value: 'px', label: 'Pixels (px)' }
              ]} />
            </Form.Item>
          </Col>
          <Col span={5}>
            <Form.Item
              name="bleeds"
              label="Bleeds"
              tooltip="Bleed area in selected units"
            >
              <Input type="number" min={0} />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* HTML Editor */}
      <Card title="HTML Template" className="mb-4">
        <CodeEditor
          language="html"
          value={html}
          onChange={handleHtmlChange}
          height="400px"
        />
      </Card>

      {/* Template Fields */}
      <Card 
        title="Template Fields" 
        className="mb-4"
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={handleAddField}
          >
            Add Field
          </Button>
        }
      >
        {fields.map((field, index) => (
          <Row key={index} gutter={16} className="mb-4 pb-4 border-b border-gray-800">
            <Col span={8}>
              <Form.Item label="Field Name" required>
                <Input
                  value={field.name}
                  onChange={e => handleFieldChange(index, {...field, name: e.target.value})}
                  placeholder="e.g., client_name"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="Display Label" required>
                <Input
                  value={field.label}
                  onChange={e => handleFieldChange(index, {...field, label: e.target.value})}
                  placeholder="e.g., Client Name"
                />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label=" ">
                <Checkbox
                  checked={field.required}
                  onChange={e => handleFieldChange(index, {...field, required: e.target.checked})}
                >
                  Required
                </Checkbox>
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label=" ">
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDeleteField(index)}
                />
              </Form.Item>
            </Col>
          </Row>
        ))}
        {fields.length === 0 && (
          <div className="text-center py-4 text-gray-500">
            No fields added yet. Click "Add Field" to create form fields for your template.
          </div>
        )}
      </Card>

      {/* Asset Manager */}
      <Card title="Assets" className="mb-4">
        <AssetManager
          templateId={templateId}
          pageId={pageId}
          assets={assets}
          onAssetsChange={setAssets}
        />
      </Card>
    </Form>
  );
};

export default PageForm;

const DEFAULT_HTML_TEMPLATE = `<!DOCTYPE html>
<html>
<head>
  <title>Document Template</title>
  <style>
    body { font-family: sans-serif; margin: 0; }
    .content { padding: 20mm; }
  </style>
</head>
<body>
  <div class="content">
    <h1>{{title}}</h1>
    <p>Hello, {{name}}!</p>
  </div>
</body>
</html>`; 