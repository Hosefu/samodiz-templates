import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import router from './routes'
import './index.css'
import { Toaster } from 'react-hot-toast'

// Error boundary component
const ErrorBoundary = ({ children }) => {
  const [error, setError] = useState(null);

  useEffect(() => {
    // Global error handler
    const handleError = (event) => {
      console.error('Global error:', event.error);
      console.error('Error stack:', event.error?.stack);
      setError(event.error.toString());
      event.preventDefault();
    };

    // Add error listener
    window.addEventListener('error', handleError);
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled rejection:', event.reason);
      console.error('Rejection stack:', event.reason?.stack);
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
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{error}</pre>
      </div>
    );
  }

  return children;
};

// Добавляем отладочную информацию
console.log('Initializing application...');
console.log('Router configuration:', router);

// Основной рендер приложения с RouterProvider и Toaster
try {
  console.log('Attempting to render application...');
  const root = document.getElementById('root');
  console.log('Root element:', root);
  
  if (!root) {
    throw new Error('Root element not found in the DOM');
  }

  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <ErrorBoundary>
        <AuthProvider>
          <RouterProvider router={router} />
          <Toaster 
            position="bottom-right"
            toastOptions={{
              duration: 5000,
              style: {
                background: '#333',
                color: '#fff',
              },
              success: {
                duration: 3000,
                theme: {
                  primary: 'green',
                  secondary: 'black',
                },
                style: {
                  background: '#10B981',
                  color: 'white',
                },
                iconTheme: {
                  primary: 'white',
                  secondary: '#10B981',
                },
              },
              error: {
                style: {
                  background: '#EF4444',
                  color: 'white',
                },
                iconTheme: {
                  primary: 'white',
                  secondary: '#EF4444',
                },
              }
            }}
          />
        </AuthProvider>
      </ErrorBoundary>
    </React.StrictMode>
  );
  console.log('Application rendered successfully');
} catch (error) {
  console.error('Fatal error during application initialization:', error);
  console.error('Error stack:', error.stack);
}