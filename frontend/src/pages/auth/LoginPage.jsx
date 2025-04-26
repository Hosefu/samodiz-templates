import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated, authError } = useAuth();
  const navigate = useNavigate();

  // При загрузке проверяем доступность API
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        await axios.get('/api/health/');
        setApiStatus('API доступен');
      } catch (error) {
        console.error('API check error:', error);
        setApiStatus(`Ошибка API: ${error.message}. Проверьте сетевое соединение.`);
      }
    };
    
    checkApiStatus();
  }, []);

  // Если пользователь уже авторизован, перенаправляем на главную
  if (isAuthenticated) {
    return <Navigate to="/" />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const success = await login(username, password);
      if (success) {
        navigate('/');
      } else {
        setError(authError || 'Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        
        {apiStatus && apiStatus !== 'API доступен' && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{apiStatus}</span>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          
          {/* Debug information */}
          <div className="mt-4 p-4 border border-gray-300 rounded bg-gray-50">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Debug Info:</h3>
            <p className="text-xs text-gray-600">API Status: {apiStatus || 'Checking...'}</p>
            <p className="text-xs text-gray-600">Auth Error: {authError || 'None'}</p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage; 