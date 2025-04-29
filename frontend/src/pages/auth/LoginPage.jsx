import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Typography, Form, Alert } from 'antd';
import { LoginOutlined } from '@ant-design/icons';
import { Button, Input, Card } from '../../components/ui/UIComponents';
import * as text from '../../constants/ux-writing';
import { useAuth } from '../../context/AuthContext';

const LoginPage = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const { login, authError } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Определяем, куда перенаправить пользователя после входа
  const from = location.state?.from?.pathname || '/admin/dashboard';
  
  const handleSubmit = async (values) => {
    setLoading(true);
    setError('');
    
    try {
      console.log('Attempting login with credentials:', values.username);
      
      const success = await login(values.username, values.password);
      
      if (success) {
        console.log('Login successful, redirecting to:', from);
        navigate(from, { replace: true });
      } else {
        console.error('Login failed');
        setError('Ошибка входа. Проверьте имя пользователя и пароль.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Не удалось войти в систему');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#111111]">
      <Card className="w-full max-w-md">
        <div className="text-center mb-6">
          <Typography.Title level={3} className="text-white">
            Document Generator
          </Typography.Title>
          <Typography.Text className="text-gray-400">
            Войдите в систему для доступа к генератору документов
          </Typography.Text>
        </div>
        
        {(error || authError) && (
          <Alert
            message="Ошибка аутентификации"
            description={error || authError}
            type="error"
            showIcon
            className="mb-4"
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ remember: true }}
        >
          <Form.Item
            name="username"
            label="Имя пользователя"
            rules={[{ required: true, message: 'Пожалуйста, введите имя пользователя!' }]}
          >
            <Input placeholder="Имя пользователя" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Пароль"
            rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
          >
            <Input.Password placeholder="Пароль" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full"
              icon={<LoginOutlined />}
              isLoading={loading}
            >
              Войти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage; 