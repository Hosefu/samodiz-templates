import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Инициализация при загрузке приложения
  useEffect(() => {
    console.log('AuthProvider: Initializing...');
    const storedTokens = JSON.parse(localStorage.getItem('tokens'));
    if (storedTokens) {
      try {
        // Проверяем, не истек ли токен доступа
        const decodedToken = jwtDecode(storedTokens.access);
        const currentTime = Date.now() / 1000;
        
        if (decodedToken.exp > currentTime) {
          setTokens(storedTokens);
          setUser(storedTokens.user);
          console.log("AuthProvider: Authorized with stored token:", storedTokens.user);
        } else {
          // Токен истек, пробуем обновить
          console.log("AuthProvider: Token expired, attempting refresh");
          refreshToken(storedTokens.refresh);
        }
      } catch (error) {
        console.error('AuthProvider: Error decoding token:', error);
        setAuthError("Ошибка декодирования токена: " + error.message);
        logout();
      }
    } else {
      console.log("AuthProvider: No stored token found");
    }
    setLoading(false);
  }, []);

  // Настройка axios с JWT
  useEffect(() => {
    if (tokens) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      console.log("AuthProvider: Set Authorization header:", `Bearer ${tokens.access.substring(0, 15)}...`);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      console.log("AuthProvider: Removed Authorization header");
    }
  }, [tokens]);

  // Обновление токена
  const refreshToken = async (refreshToken) => {
    try {
      console.log("AuthProvider: Requesting token refresh");
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
      
      console.log("AuthProvider: Token successfully refreshed");
      setTokens(updatedTokens);
      localStorage.setItem('tokens', JSON.stringify(updatedTokens));
      return true;
    } catch (error) {
      console.error('AuthProvider: Error refreshing token:', error);
      console.error('AuthProvider: Error response data:', error.response?.data);
      setAuthError("Ошибка обновления токена: " + (error.response?.data?.detail || error.response?.data?.error || error.message));
      logout();
      return false;
    }
  };

  // Авторизация пользователя
  const login = async (username, password) => {
    try {
      console.log("AuthProvider: Attempting login for user:", username);
      const response = await axios.post('/api/auth/login/', {
        username,
        password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log("AuthProvider: Successful login response:", response.data);
      
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
      console.error('AuthProvider: Login error:', error);
      console.error('AuthProvider: Error response:', error.response?.data);
      setAuthError("Ошибка входа: " + errorMessage);
      return false;
    }
  };

  // Выход из системы
  const logout = async () => {
    console.log("AuthProvider: Logging out");
    if (tokens && tokens.refresh) {
      try {
        await axios.post('/api/auth/logout/', {
          refresh: tokens.refresh
        });
        console.log("AuthProvider: Successful logout");
      } catch (error) {
        console.error('AuthProvider: Error during logout:', error);
      }
    }
    
    setTokens(null);
    setUser(null);
    localStorage.removeItem('tokens');
    // Удаляем навигацию, так как она должна быть в компонентах
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