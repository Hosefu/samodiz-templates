import { createBrowserRouter } from 'react-router-dom';
import AdminLayout from '../components/layout/AdminLayout';
import Dashboard from '../pages/admin/Dashboard';
import TemplateList from '../pages/admin/TemplateList';
import TemplateEdit from '../pages/admin/TemplateEdit';
import TemplateCreate from '../pages/admin/TemplateCreate';
import PageEdit from '../pages/admin/PageEdit';
import PageCreate from '../pages/admin/PageCreate';
import PublicLayout from '../components/layout/PublicLayout';
import Home from '../pages/public/Home';
import LoginPage from '../pages/auth/LoginPage';
import PrivateRoute from '../components/auth/PrivateRoute';

const router = createBrowserRouter([
  {
    path: "/admin",
    element: (
      <PrivateRoute requireAdmin={true}>
        <AdminLayout />
      </PrivateRoute>
    ),
    children: [
      { path: "", element: <Dashboard /> },
      { path: "templates", element: <TemplateList /> },
      { path: "templates/new", element: <TemplateCreate /> },
      { path: "templates/:id", element: <TemplateEdit /> },
      { path: "templates/:templateId/pages/new", element: <PageCreate /> },
      { path: "templates/:templateId/pages/:pageId", element: <PageEdit /> },
    ]
  },
  {
    path: "/",
    element: <PublicLayout />,
    children: [
      { path: "", element: <Home /> },
      { path: "login", element: <LoginPage /> }
    ]
  }
]);

export default router; 