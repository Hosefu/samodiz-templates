import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import router from './routes'

// Error boundary component
const ErrorBoundary = ({ children }) => {
  const [error, setError] = useState(null);

  useEffect(() => {
    // Global error handler
    const handleError = (event) => {
      console.error('Global error:', event.error);
      setError(event.error.toString());
      event.preventDefault();
    };

    // Add error listener
    window.addEventListener('error', handleError);
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled rejection:', event.reason);
      setError(`Promise error: ${event.reason}`);
      event.preventDefault();
    });

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleError);
    };
  }, []);

  if (error) {
    return (
      <div style={{ 
        padding: '20px', 
        margin: '20px', 
        backgroundColor: '#ffebee', 
        border: '1px solid #f44336',
        borderRadius: '4px' 
      }}>
        <h2>Произошла ошибка:</h2>
        <pre>{error}</pre>
      </div>
    );
  }

  return children;
};

// Создаем wrapper для админ-панели
const AdminApp = () => (
  <ErrorBoundary>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </ErrorBoundary>
);

// Рендерим приложение админ-панели
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AdminApp />
  </React.StrictMode>
) 