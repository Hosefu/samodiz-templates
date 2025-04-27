import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Layout, Menu, Typography, Avatar, Dropdown, Divider
} from 'antd';
import {
  DashboardOutlined,
  FileOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  SettingOutlined,
  BellOutlined
} from '@ant-design/icons';
import { logoutUser } from '../../redux/slices/authSlice';
import { TemplateProvider } from '../../context/TemplateContext';

const { Header, Sider, Content } = Layout;

const AdminLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector(state => state.auth);
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = async () => {
    try {
      await dispatch(logoutUser()).unwrap();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const userMenu = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
      onClick: () => navigate('/admin/profile')
    },
    {
      key: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
      onClick: () => navigate('/admin/settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: handleLogout
    }
  ];

  return (
    <TemplateProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          style={{ 
            background: '#0A0A0A',
            boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
          }}
        >
          <div className="logo" style={{ 
            height: '64px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: collapsed ? 'center' : 'flex-start',
            padding: collapsed ? '0' : '0 24px',
            borderBottom: '1px solid #222'
          }}>
            {collapsed ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="24" height="24" rx="6" fill="#3B82F6"/>
                <path d="M6 6V18H18V6H6ZM16 8V12H8V8H16ZM8 16V14H16V16H8Z" fill="white"/>
              </svg>
            ) : (
              <Typography.Title level={4} style={{ margin: 0, color: 'white' }}>
                Document Gen
              </Typography.Title>
            )}
          </div>
          
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname.split('/')[2] || 'dashboard']}
            style={{ background: '#0A0A0A', borderRight: 0 }}
            items={[
              {
                key: 'dashboard',
                icon: <DashboardOutlined />,
                label: 'Dashboard',
                onClick: () => navigate('/admin/dashboard')
              },
              {
                key: 'templates',
                icon: <FileOutlined />,
                label: 'Templates',
                onClick: () => navigate('/admin/templates')
              }
            ]}
          />
        </Sider>
        
        <Layout>
          <Header style={{ 
            padding: '0 16px', 
            background: '#111111', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            height: '64px',
            borderBottom: '1px solid #222'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
                className: 'trigger',
                onClick: () => setCollapsed(!collapsed),
                style: { color: '#fff', fontSize: '18px', cursor: 'pointer' }
              })}
              <Typography.Title level={4} style={{ margin: '0 0 0 16px', color: 'white' }}>
                {location.pathname.includes('/templates') ? 'Templates' : 
                 location.pathname.includes('/dashboard') ? 'Dashboard' : 'Admin Panel'}
              </Typography.Title>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <BellOutlined style={{ color: '#fff', fontSize: '18px', marginRight: '24px', cursor: 'pointer' }} />
              
              <Dropdown menu={{ items: userMenu }} placement="bottomRight" arrow>
                <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                  <Avatar style={{ backgroundColor: '#3B82F6' }} icon={<UserOutlined />} />
                  {!collapsed && (
                    <Typography.Text style={{ margin: '0 0 0 8px', color: 'white' }}>
                      {user?.username || 'Admin'}
                    </Typography.Text>
                  )}
                </div>
              </Dropdown>
            </div>
          </Header>
          
          <Content style={{ 
            margin: '24px 16px', 
            padding: 24, 
            minHeight: 280, 
            background: '#111111',
            borderRadius: '8px'
          }}>
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </TemplateProvider>
  );
};

export default AdminLayout; 