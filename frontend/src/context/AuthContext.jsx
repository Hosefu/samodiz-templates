import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const navigate = useNavigate();

  // Инициализация при загрузке приложения
  useEffect(() => {
    const storedTokens = JSON.parse(localStorage.getItem('tokens'));
    if (storedTokens) {
      try {
        // Проверяем, не истек ли токен доступа
        const decodedToken = jwtDecode(storedTokens.access);
        const currentTime = Date.now() / 1000;
        
        if (decodedToken.exp > currentTime) {
          setTokens(storedTokens);
          setUser(storedTokens.user);
          console.log("Авторизован с сохраненным токеном:", storedTokens.user);
        } else {
          // Токен истек, пробуем обновить
          console.log("Токен истек, пробуем обновить");
          refreshToken(storedTokens.refresh);
        }
      } catch (error) {
        console.error('Error decoding token:', error);
        setAuthError("Ошибка декодирования токена: " + error.message);
        logout();
      }
    } else {
      console.log("Нет сохраненного токена");
    }
    setLoading(false);
  }, []);

  // Настройка axios с JWT
  useEffect(() => {
    if (tokens) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      console.log("Установлен заголовок Authorization:", `Bearer ${tokens.access.substring(0, 15)}...`);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      console.log("Удален заголовок Authorization");
    }
  }, [tokens]);

  // Обновление токена
  const refreshToken = async (refreshToken) => {
    try {
      console.log("Запрос на обновление токена");
      const response = await axios.post('/api/auth/refresh/', {
        refresh: refreshToken
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const updatedTokens = {
        ...tokens,
        access: response.data.access
      };
      
      console.log("Токен успешно обновлен");
      setTokens(updatedTokens);
      localStorage.setItem('tokens', JSON.stringify(updatedTokens));
      return true;
    } catch (error) {
      console.error('Error refreshing token:', error);
      console.error('Error response data:', error.response?.data);
      setAuthError("Ошибка обновления токена: " + (error.response?.data?.detail || error.response?.data?.error || error.message));
      logout();
      return false;
    }
  };

  // Авторизация пользователя
  const login = async (username, password) => {
    try {
      console.log("Попытка входа для пользователя:", username);
      const response = await axios.post('/api/auth/login/', {
        username,
        password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log("Успешный ответ авторизации:", response.data);
      
      const tokenData = {
        access: response.data.access,
        refresh: response.data.refresh,
        user: response.data.user
      };
      
      setTokens(tokenData);
      setUser(response.data.user);
      setAuthError(null);
      localStorage.setItem('tokens', JSON.stringify(tokenData));
      
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || error.message;
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      setAuthError("Ошибка входа: " + errorMessage);
      return false;
    }
  };

  // Выход из системы
  const logout = async () => {
    console.log("Выполняется выход из системы");
    if (tokens && tokens.refresh) {
      try {
        await axios.post('/api/auth/logout/', {
          refresh: tokens.refresh
        });
        console.log("Успешный выход из системы");
      } catch (error) {
        console.error('Error during logout:', error);
      }
    }
    
    setTokens(null);
    setUser(null);
    localStorage.removeItem('tokens');
    navigate('/login');
  };

  // Проверка доступа к администрированию
  const hasAdminAccess = () => {
    return user && (user.is_admin || user.role === 'admin');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authError,
        login,
        logout,
        refreshToken,
        hasAdminAccess,
        isAuthenticated: !!user
      }}
    >
      {authError && (
        <div style={{ 
          position: 'fixed', 
          top: '20px', 
          right: '20px',
          backgroundColor: '#f8d7da', 
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          padding: '10px',
          zIndex: 9999,
          maxWidth: '400px'
        }}>
          <h3 style={{ margin: '0 0 5px 0' }}>Ошибка авторизации:</h3>
          <p style={{ margin: 0 }}>{authError}</p>
        </div>
      )}
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 