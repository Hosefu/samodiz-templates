import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PrivateRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, user, hasAdminAccess } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // Перенаправляем на страницу входа, сохраняя текущий путь
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !hasAdminAccess()) {
    // Если требуется админ, но пользователь не админ
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute; 