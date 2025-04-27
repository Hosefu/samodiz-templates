import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { TemplateProvider } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { LayoutDashboard, Files, LogOut } from 'lucide-react';

const AdminLayout = () => {
  const location = useLocation();
  
  const getHeaderTitle = () => {
    const path = location.pathname;
    if (path === '/admin/dashboard') return text.ADMIN_HEADER_DASHBOARD;
    if (path.startsWith('/admin/templates/new')) return text.ADMIN_HEADER_CREATE;
    if (path.startsWith('/admin/templates/') && path.includes('/pages/')) return text.ADMIN_HEADER_EDIT;
    if (path.startsWith('/admin/templates/')) return text.ADMIN_HEADER_TEMPLATES;
    return text.APP_TITLE;
  };

  const isActive = (path) => {
    if (path === '/admin/dashboard') {
      return location.pathname === path ? 'bg-blue-700 text-white' : 'text-blue-100 hover:bg-blue-700 hover:text-white';
    }
    return location.pathname.startsWith(path) ? 'bg-blue-700 text-white' : 'text-blue-100 hover:bg-blue-700 hover:text-white';
  };

  return (
    <TemplateProvider>
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar */}
        <aside className="w-64 bg-blue-800 text-white flex flex-col">
          <div className="p-5 border-b border-blue-700">
            <h1 className="text-2xl font-semibold text-center">{text.ADMIN_SIDEBAR_TITLE}</h1>
          </div>
          <nav className="flex-grow mt-6 space-y-1 px-2">
            <Link
              to="/admin/dashboard" 
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/admin/dashboard')}`}
            >
              <LayoutDashboard className="mr-3 h-5 w-5" />
              {text.ADMIN_SIDEBAR_DASHBOARD}
            </Link>
            <Link
              to="/admin/templates" 
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/admin/templates')}`}
            >
              <Files className="mr-3 h-5 w-5" />
              {text.ADMIN_SIDEBAR_TEMPLATES}
            </Link>
          </nav>
          <div className="p-4 border-t border-blue-700 mt-auto">
             <a 
               href="/" 
               className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-blue-100 hover:bg-blue-700 hover:text-white transition-colors"
             >
               <LogOut className="mr-3 h-5 w-5 transform rotate-180" />
               {text.ADMIN_SIDEBAR_BACK_TO_PUBLIC}
             </a>
          </div>
        </aside>
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800">
                {getHeaderTitle()}
              </h2>
            </div>
          </header>
          <main className="flex-1 overflow-auto p-6 bg-gray-50">
            <Outlet />
          </main>
        </div>
      </div>
    </TemplateProvider>
  );
};

export default AdminLayout; 