import React, { useState, useEffect } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import './App.css';
import * as text from './constants/ux-writing'; // Исправляем путь

// Диагностический компонент
const Diagnostics = () => {
  const { user, isAuthenticated, authError } = useAuth();
  const location = useLocation();
  const [apiStatus, setApiStatus] = useState(text.DIAG_API_CHECKING);
  
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch('/api/health/');
        if (response.ok) {
          setApiStatus(text.DIAG_API_AVAILABLE);
        } else {
          setApiStatus(text.DIAG_API_UNAVAILABLE(response.status, response.statusText));
        }
      } catch (error) {
        setApiStatus(text.DIAG_API_ERROR(error.message));
      }
    };
    
    checkApi();
  }, []);
  
  return (
    <div className="diagnostics" style={{ 
      position: 'fixed', 
      bottom: '10px', 
      right: '10px',
      backgroundColor: 'rgba(248, 249, 250, 0.9)',
      border: '1px solid #ddd',
      borderRadius: '4px',
      padding: '8px 12px',
      zIndex: 9999,
      maxWidth: '350px',
      fontSize: '11px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{margin: '0 0 4px 0', fontSize: '12px', fontWeight: '600'}}>{text.DIAG_TITLE}</h3>
      <div>{text.DIAG_CURRENT_PATH} <strong>{location.pathname}</strong></div>
      <div>{text.DIAG_AUTH_STATUS} <strong>{isAuthenticated ? text.DIAG_AUTH_YES : text.DIAG_AUTH_NO}</strong></div>
      <div>{text.DIAG_API_STATUS} <strong>{apiStatus}</strong></div>
      {authError && <div style={{color: '#dc2626'}}>{text.DIAG_ERROR_PREFIX} {authError}</div>}
      {user && <div>{text.DIAG_USER_INFO(user.username, user.role || (user.is_admin ? text.DIAG_USER_ROLE_ADMIN : text.DIAG_USER_ROLE_USER))}</div>}
    </div>
  );
};

// Навигация
const Navigation = () => {
  const { isAuthenticated, logout, user, hasAdminAccess } = useAuth();
  
  return (
    <nav className="bg-white text-gray-800 p-4 shadow-md border-b border-gray-200">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="font-bold text-xl text-blue-600">{text.APP_TITLE}</Link>
        <ul className="flex space-x-6 items-center">
          <li><Link to="/" className="text-gray-600 hover:text-blue-600 transition-colors">{text.NAV_HOME}</Link></li>
          {isAuthenticated ? (
            <>
              {hasAdminAccess() && (
                 <li><Link to="/admin/dashboard" className="text-gray-600 hover:text-blue-600 transition-colors">{text.NAV_ADMIN}</Link></li>
              )}
              {user && <li className='text-sm text-gray-500'>{text.NAV_GREETING(user.username)}</li>}
              <li><button onClick={logout} className="text-sm text-red-600 hover:text-red-800 transition-colors">{text.NAV_LOGOUT}</button></li>
            </>
          ) : (
            <li><Link to="/login" className="text-gray-600 hover:text-blue-600 transition-colors">{text.NAV_LOGIN}</Link></li>
          )}
        </ul>
      </div>
    </nav>
  );
};

// Основной компонент App теперь очень простой
const App = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Diagnostics />
      <Navigation />
      
      <main className="flex-grow">
         <Outlet />
      </main>
    </div>
  );
};

export default App;