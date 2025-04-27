import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { ConfigProvider, App as AntApp } from 'antd';
import { store, persistor } from './redux/store';
import { AuthProvider } from './context/AuthContext';
import App from './App';
import './index.css';
import { Toaster } from 'react-hot-toast';
import themeConfig from './theme/themeConfig';

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

// Основной рендер приложения с RouterProvider и Toaster
try {
  const root = document.getElementById('root');
  
  if (!root) {
    throw new Error('Root element not found in the DOM');
  }

  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <ErrorBoundary>
        <Provider store={store}>
          <PersistGate loading={null} persistor={persistor}>
            <ConfigProvider theme={themeConfig}>
              <AuthProvider>
                <AntApp>
                  <BrowserRouter>
                    <App />
                    <Toaster 
                      position="bottom-right"
                      toastOptions={{
                        duration: 5000,
                        style: {
                          background: '#222222',
                          color: '#fff',
                        },
                        success: {
                          style: {
                            background: '#10B981',
                            color: 'white',
                          },
                        },
                        error: {
                          style: {
                            background: '#EF4444',
                            color: 'white',
                          },
                        }
                      }}
                    />
                  </BrowserRouter>
                </AntApp>
              </AuthProvider>
            </ConfigProvider>
          </PersistGate>
        </Provider>
      </ErrorBoundary>
    </React.StrictMode>
  );
} catch (error) {
  console.error('Fatal error during application initialization:', error);
  console.error('Error stack:', error.stack);
}