import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { TemplateProvider } from '../../context/TemplateContext';

const AdminLayout = () => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname.startsWith(path) ? 'bg-blue-700' : '';
  };

  return (
    <TemplateProvider>
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar */}
        <div className="w-64 bg-blue-800 text-white">
          <div className="p-4">
            <h1 className="text-2xl font-semibold">Admin Panel</h1>
          </div>
          <nav className="mt-6">
            <Link 
              to="/" 
              className={`flex items-center px-4 py-2 hover:bg-blue-700 ${location.pathname === '/' ? 'bg-blue-700' : ''}`}
            >
              Dashboard
            </Link>
            <Link 
              to="/templates" 
              className={`flex items-center px-4 py-2 hover:bg-blue-700 ${isActive('/templates') ? 'bg-blue-700' : ''}`}
            >
              Templates
            </Link>
            <a 
              href="/" 
              className="flex items-center px-4 py-2 hover:bg-blue-700 mt-10"
            >
              Back to Public Site
            </a>
          </nav>
        </div>
        
        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          <header className="bg-white shadow">
            <div className="p-4">
              <h2 className="text-xl font-semibold text-gray-800">
                {location.pathname === '/' ? 'Dashboard' : 
                 location.pathname === '/templates' ? 'Templates' :
                 location.pathname.includes('new') ? 'Create' : 'Edit'}
              </h2>
            </div>
          </header>
          <main className="p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </TemplateProvider>
  );
};

export default AdminLayout; 