import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import * as text from '../../constants/ux-writing';
import { Layout, Menu, Typography, Button, Divider, Badge } from 'antd';
import {
  HomeOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';

const { Header, Content, Footer } = Layout;

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

const PublicLayout = () => {
  const { isAuthenticated, logout, user, hasAdminAccess } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Link to="/">
            <Typography.Title level={4} style={{ margin: 0, color: 'white' }}>
              {text.APP_TITLE}
            </Typography.Title>
          </Link>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ flex: 1, justifyContent: 'flex-end' }}
          items={[
            {
              key: '/',
              icon: <HomeOutlined />,
              label: text.NAV_HOME,
              onClick: () => navigate('/')
            },
            isAuthenticated && hasAdminAccess() ? {
              key: '/admin/dashboard',
              icon: <SettingOutlined />,
              label: text.NAV_ADMIN,
              onClick: () => navigate('/admin/dashboard')
            } : null,
            isAuthenticated ? {
              key: 'user',
              icon: <UserOutlined />,
              label: text.NAV_GREETING(user?.username || ''),
              disabled: true
            } : null,
            isAuthenticated ? {
              key: 'logout',
              icon: <LogoutOutlined />,
              label: text.NAV_LOGOUT,
              onClick: logout
            } : {
              key: '/login',
              icon: <UserOutlined />,
              label: text.NAV_LOGIN,
              onClick: () => navigate('/login')
            }
          ].filter(Boolean)}
        />
      </Header>
      <Content style={{ padding: '0 50px', marginTop: 24 }}>
        <div style={{ padding: 24, minHeight: 280, backgroundColor: '#141414' }}>
          <Outlet />
        </div>
      </Content>
      <Footer style={{ textAlign: 'center', backgroundColor: '#141414', color: 'rgba(255,255,255,0.45)' }}>
        Document Generator ©{new Date().getFullYear()}
      </Footer>
    </Layout>
  );
};

export default PublicLayout; 