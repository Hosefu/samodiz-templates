import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { TemplateProvider } from '../../context/TemplateContext';
import * as text from '../../constants/ux-writing';
import { Layout, Menu, Typography, theme } from 'antd';
import { 
  DashboardOutlined, 
  FileOutlined, 
  LogoutOutlined 
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const getHeaderTitle = () => {
    const path = location.pathname;
    if (path === '/admin/dashboard') return text.ADMIN_HEADER_DASHBOARD;
    if (path.startsWith('/admin/templates/new')) return text.ADMIN_HEADER_CREATE;
    if (path.startsWith('/admin/templates/') && path.includes('/pages/')) return text.ADMIN_HEADER_EDIT;
    if (path.startsWith('/admin/templates/')) return text.ADMIN_HEADER_TEMPLATES;
    return text.APP_TITLE;
  };

  return (
    <TemplateProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          theme="dark"
          collapsible
          breakpoint="lg"
        >
          <div style={{ 
            height: 32, 
            margin: 16, 
            color: 'white', 
            textAlign: 'center',
            fontSize: '18px',
            fontWeight: 'bold'
          }}>
            {text.ADMIN_SIDEBAR_TITLE}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            defaultSelectedKeys={['dashboard']}
            selectedKeys={[location.pathname.split('/')[2] || 'dashboard']}
            items={[
              {
                key: 'dashboard',
                icon: <DashboardOutlined />,
                label: text.ADMIN_SIDEBAR_DASHBOARD,
                onClick: () => navigate('/admin/dashboard')
              },
              {
                key: 'templates',
                icon: <FileOutlined />,
                label: text.ADMIN_SIDEBAR_TEMPLATES,
                onClick: () => navigate('/admin/templates')
              },
              {
                key: 'back',
                icon: <LogoutOutlined />,
                label: text.ADMIN_SIDEBAR_BACK_TO_PUBLIC,
                onClick: () => navigate('/')
              }
            ]}
          />
        </Sider>
        <Layout>
          <Header style={{ 
            padding: '0 16px',
            background: '#002140',
            color: 'white',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Typography.Title 
              level={4} 
              style={{ margin: 0, color: 'white' }}
            >
              {getHeaderTitle()}
            </Typography.Title>
          </Header>
          <Content style={{ margin: '24px 16px', padding: 24, background: '#141414' }}>
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </TemplateProvider>
  );
};

export default AdminLayout; 