import { theme } from 'antd';
const { darkAlgorithm } = theme;

// Новая темная тема в стиле Krea.ai
const themeConfig = {
  token: {
    colorPrimary: '#3B82F6', // Синий, как на примере Krea.ai
    colorSuccess: '#10B981', // Зеленый для успешных операций
    colorError: '#EF4444',   // Красный для ошибок
    colorWarning: '#F59E0B', // Оранжевый для предупреждений
    colorInfo: '#6366F1',    // Индиго для информации
    
    // Базовые цвета темы
    colorBgBase: '#141414',      // Очень темный фон
    colorTextBase: '#F5F5F5',    // Светлый текст
    
    // Основные цвета фона
    colorBgContainer: '#1F1F1F', // Фон контейнеров
    colorBgElevated: '#262626',  // Приподнятые элементы
    colorBgLayout: '#0A0A0A',    // Фон лейаута
    
    // Границы
    colorBorder: '#333333',        // Цвет границ
    colorBorderSecondary: '#2C2C2C', // Вторичный цвет границ
    
    // Тексты
    colorText: '#D1D5DB',         // Основной текст
    colorTextSecondary: '#9CA3AF', // Вторичный текст
    colorTextTertiary: '#6B7280',  // Третичный текст
    colorTextQuaternary: '#4B5563', // Четвертичный текст
    
    // Дополнительные параметры
    borderRadius: 8,              // Закругление углов
    wireframe: false,             // Отключаем каркас
    fontSize: 14,                 // Базовый размер шрифта
  },
  components: {
    Button: {
      colorPrimary: '#3B82F6',
      algorithm: true, // Включаем автоматическое создание темных вариантов
    },
    Card: {
      colorBgContainer: '#1F1F1F',
      colorBorderSecondary: '#2C2C2C',
    },
    Input: {
      colorBgContainer: '#262626',
      colorBorder: '#333333',
    },
    Select: {
      colorBgContainer: '#262626',
      colorBorder: '#333333',
    },
    Layout: {
      colorBgHeader: '#0A0A0A', 
      colorBgBody: '#141414',
      colorBgFooter: '#0A0A0A',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorItemText: '#D1D5DB',
      colorItemTextSelected: '#3B82F6',
      colorItemBgSelected: 'rgba(59, 130, 246, 0.1)',
      colorItemTextHover: '#F5F5F5',
    },
    Table: {
      colorBgContainer: '#262626',
      colorText: '#D1D5DB',
    },
    Modal: {
      colorBgElevated: '#262626',
    },
  },
};

export default themeConfig; 