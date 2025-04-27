import React from 'react';
import { Link } from 'react-router-dom';
import { useTemplates } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { Loader2, FilePlus, Settings } from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';

const Dashboard = () => {
  const { templates, loading, error } = useTemplates();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 bg-red-100 p-4 rounded-md">{text.ADMIN_TEMPLATE_LIST_ERROR(error)}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-2xl font-bold mb-2 text-gray-800">{text.ADMIN_DASHBOARD_TITLE}</h2>
        <p className="text-gray-600">
          {text.ADMIN_DASHBOARD_WELCOME}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title={text.ADMIN_DASHBOARD_TEMPLATES_CARD_TITLE}>
          <p className="text-gray-600 mb-4">{text.ADMIN_DASHBOARD_TEMPLATES_CARD_INFO(templates.length)}</p>
          <Link to="/admin/templates">
            <Button variant="secondary" icon={<Settings />}>
              {text.ADMIN_DASHBOARD_MANAGE_TEMPLATES_BUTTON}
            </Button>
          </Link>
        </Card>

        <Card title={text.ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_TITLE}>
          <p className="text-gray-600 mb-4">{text.ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_INFO}</p>
          <Link to="/admin/templates/new">
            <Button variant="default" icon={<FilePlus />}>
              {text.ADMIN_DASHBOARD_CREATE_TEMPLATE_BUTTON}
            </Button>
          </Link>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard; 