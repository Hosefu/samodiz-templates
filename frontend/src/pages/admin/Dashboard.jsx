import React from 'react';
import { Link } from 'react-router-dom';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { 
  Button, Card, Space, Typography, Spin, Alert 
} from '../../components/ui/AntComponents';
import { 
  FileAddOutlined, SettingOutlined 
} from '@ant-design/icons';

const Dashboard = () => {
  const { templates, loading, error } = useTemplates();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Ошибка"
        description={text.ADMIN_TEMPLATE_LIST_ERROR(error)}
        type="error"
        showIcon
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <Typography.Title level={2} style={{ marginBottom: 16 }}>
          {text.ADMIN_DASHBOARD_TITLE}
        </Typography.Title>
        <Typography.Text type="secondary">
          {text.ADMIN_DASHBOARD_WELCOME}
        </Typography.Text>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title={text.ADMIN_DASHBOARD_TEMPLATES_CARD_TITLE}>
          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
            {text.ADMIN_DASHBOARD_TEMPLATES_CARD_INFO(templates.length)}
          </Typography.Text>
          <Link to="/admin/templates">
            <Button variant="secondary" icon={<SettingOutlined />}>
              {text.ADMIN_DASHBOARD_MANAGE_TEMPLATES_BUTTON}
            </Button>
          </Link>
        </Card>

        <Card title={text.ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_TITLE}>
          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
            {text.ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_INFO}
          </Typography.Text>
          <Link to="/admin/templates/new">
            <Button variant="default" icon={<FileAddOutlined />}>
              {text.ADMIN_DASHBOARD_CREATE_TEMPLATE_BUTTON}
            </Button>
          </Link>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard; 