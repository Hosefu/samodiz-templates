import React from 'react';
import { Typography, Card, Space } from 'antd';
import { useAuth } from '../../context/AuthContext';
import * as text from '../../constants/ux-writing';

const { Title, Paragraph } = Typography;

const Home = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={2}>Добро пожаловать в Document Generator</Title>
            <Paragraph>
              {isAuthenticated 
                ? `Привет, ${user?.username || 'пользователь'}!`
                : 'Пожалуйста, войдите в систему для доступа к функциям генератора документов.'}
            </Paragraph>
          </div>

          <div>
            <Title level={3}>О системе</Title>
            <Paragraph>
              Document Generator - это мощный инструмент для создания и управления шаблонами документов.
              Вы можете создавать шаблоны в различных форматах, включая PDF, DOCX, XLSX и другие.
            </Paragraph>
          </div>

          <div>
            <Title level={3}>Основные возможности</Title>
            <ul>
              <li>Создание и редактирование шаблонов документов</li>
              <li>Поддержка различных форматов (PDF, DOCX, XLSX, HTML)</li>
              <li>Управление полями и переменными в шаблонах</li>
              <li>Загрузка и управление ресурсами (изображения, шрифты)</li>
              <li>Предпросмотр и тестирование шаблонов</li>
            </ul>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default Home;
