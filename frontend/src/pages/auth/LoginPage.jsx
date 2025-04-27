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
    const checkApiStatus = async () => {
      try {
        await axios.get('/api/health/');
        setApiStatus(text.API_AVAILABLE_MSG);
      } catch (error) {
        console.error('API check error:', error);
        setApiStatus(text.DIAG_API_ERROR(error.message));
      }
    };
    
    checkApiStatus();
  }, []);

  // Если пользователь уже авторизован, перенаправляем на главную
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const success = await login(username, password);
      if (success) {
        navigate('/', { replace: true });
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="max-w-md w-full" title={text.LOGIN_PAGE_TITLE}>
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 rounded-md text-sm" role="alert">
            {error}
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