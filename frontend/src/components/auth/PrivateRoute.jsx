import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PrivateRoute = ({ children, requireAdmin = false }) => {
  const { user, isAuthenticated, loading } = useAuth();

  // Отображение загрузки, пока проверяем аутентификацию
  if (loading) {
    return <div>Загрузка...</div>;
  }

  // Проверка аутентификации
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Проверка прав администратора, если требуется
  if (requireAdmin && !(user.is_admin || user.role === 'admin')) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute; 