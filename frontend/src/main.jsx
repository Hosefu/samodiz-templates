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

// Основной рендер приложения с RouterProvider и Toaster
ReactDOM.createRoot(document.getElementById('root')).render(
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
)