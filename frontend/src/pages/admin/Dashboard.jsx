import React from 'react';
import { Link } from 'react-router-dom';
import { useTemplates } from '../../context/TemplateContext';

const Dashboard = () => {
  const { templates, loading, error } = useTemplates();

  if (loading) return <div className="text-center">Loading...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Document Generator Dashboard</h2>
        <p className="text-gray-600">
          Welcome to the admin panel. Here you can manage your templates and generate documents.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Templates</h3>
          <p className="text-gray-600 mb-4">You have {templates.length} templates in your system.</p>
          <Link
            to="/admin/templates"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Manage Templates
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Create New Template</h3>
          <p className="text-gray-600 mb-4">Start by creating a new template for your documents.</p>
          <Link
            to="/admin/templates/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            Create Template
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 