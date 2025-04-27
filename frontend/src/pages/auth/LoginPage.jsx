import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import * as text from '../../constants/ux-writing';
import { LogIn } from 'lucide-react';

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
    console.log('LoginPage: Checking API status...');
    const checkApiStatus = async () => {
      try {
        const response = await axios.get('/api/health/');
        console.log('LoginPage: API health check response:', response.data);
        setApiStatus(text.API_AVAILABLE_MSG);
      } catch (error) {
        console.error('LoginPage: API check error:', error);
        setApiStatus(text.DIAG_API_ERROR(error.message));
      }
    };
    
    checkApiStatus();
  }, []);

  // Если пользователь уже авторизован, перенаправляем на главную
  if (isAuthenticated) {
    console.log('LoginPage: User is already authenticated, redirecting to home');
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      console.log('LoginPage: Attempting login...');
      const success = await login(username, password);
      if (success) {
        console.log('LoginPage: Login successful, redirecting to home');
        navigate('/', { replace: true });
      } else {
        console.error('LoginPage: Login failed:', authError);
        setError(authError || 'Invalid credentials. Please try again.');
      }
    } catch (err) {
      console.error('LoginPage: Unexpected error during login:', err);
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="max-w-md w-full" title={text.LOGIN_PAGE_TITLE}>
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 rounded-md text-sm" role="alert">
            {error}
          </div>
        )}
        
        {apiStatus && (
          <div className="bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 mb-4 rounded-md text-sm" role="status">
            {apiStatus}
          </div>
        )}
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            label={text.LOGIN_USERNAME_LABEL}
            id="username"
            name="username"
            type="text"
            required
            placeholder={text.LOGIN_USERNAME_LABEL.replace(':', '')}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <Input
            label={text.LOGIN_PASSWORD_LABEL}
            id="password"
            name="password"
            type="password"
            required
            placeholder={text.LOGIN_PASSWORD_LABEL.replace(':', '')}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div className="pt-2">
            <Button
              type="submit"
              isLoading={loading}
              className="w-full"
              icon={<LogIn />}
            >
              {text.LOGIN_SUBMIT_BUTTON}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default LoginPage; 