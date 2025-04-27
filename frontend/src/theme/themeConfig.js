import { theme } from 'antd';
const { darkAlgorithm } = theme;

// Новая темная тема в стиле Krea.ai
const themeConfig = {
  algorithm: darkAlgorithm,
  token: {
    // Base colors
    colorPrimary: '#3B82F6', // Bright blue
    colorSuccess: '#10B981', // Green
    colorError: '#EF4444',   // Red
    colorWarning: '#F59E0B', // Amber
    colorInfo: '#6366F1',    // Indigo
    
    // Background colors
    colorBgBase: '#111111',        // Base background
    colorBgContainer: '#1A1A1A',   // Container background
    colorBgElevated: '#222222',    // Elevated elements
    colorBgLayout: '#0A0A0A',      // Layout background
    
    // Border colors
    colorBorder: '#333333',        // Border
    colorBorderSecondary: '#2C2C2C', // Secondary border
    
    // Text colors
    colorText: '#F3F4F6',          // Primary text
    colorTextSecondary: '#D1D5DB', // Secondary text
    colorTextTertiary: '#9CA3AF',  // Tertiary text
    
    // Component styles
    borderRadius: 8,               // Border radius
    wireframe: false,              // Disable wireframe
    fontSize: 14,                  // Base font size
  },
  components: {
    Button: {
      colorPrimary: '#3B82F6',
      algorithm: true,
    },
    Card: {
      colorBgContainer: '#1A1A1A',
      colorBorderSecondary: '#2C2C2C',
    },
    Input: {
      colorBgContainer: '#222222',
      colorBorder: '#333333',
    },
    Select: {
      colorBgContainer: '#222222',
      colorBorder: '#333333',
    },
    Layout: {
      colorBgHeader: '#0A0A0A',
      colorBgBody: '#111111',
      colorBgFooter: '#0A0A0A',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorItemText: '#D1D5DB',
      colorItemTextSelected: '#3B82F6',
      colorItemBgSelected: 'rgba(59, 130, 246, 0.1)',
    },
    Table: {
      colorBgContainer: '#1A1A1A',
      colorText: '#D1D5DB',
    },
    Modal: {
      colorBgElevated: '#1A1A1A',
    },
    Form: {
      colorText: '#F3F4F6',
    },
  },
};

export default themeConfig; 