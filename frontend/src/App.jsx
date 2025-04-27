import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import PrivateRoute from './components/auth/PrivateRoute';
import PublicLayout from './components/layout/PublicLayout';
import AdminLayout from './components/layout/AdminLayout';
import Home from './pages/public/Home';
import LoginPage from './pages/auth/LoginPage';
import Dashboard from './pages/admin/Dashboard';
import TemplateList from './pages/admin/TemplateList';
import TemplateCreate from './pages/admin/TemplateCreate';
import TemplateEdit from './pages/admin/TemplateEdit';
import PageCreate from './pages/admin/PageCreate';
import PageEdit from './pages/admin/PageEdit';

const App = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<LoginPage />} />
      </Route>
      
      <Route 
        path="/admin" 
        element={
          <PrivateRoute requireAdmin>
            <AdminLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="templates" element={<TemplateList />} />
        <Route path="templates/new" element={<TemplateCreate />} />
        <Route path="templates/:id" element={<TemplateEdit />} />
        <Route path="templates/:templateId/pages/new" element={<PageCreate />} />
        <Route path="templates/:templateId/pages/:pageId" element={<PageEdit />} />
      </Route>
    </Routes>
  );
};

export default App; 