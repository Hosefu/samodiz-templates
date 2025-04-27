import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Typography, Form, Alert, Space } from 'antd';
import { LoginOutlined } from '@ant-design/icons';
import { loginUser } from '../../redux/slices/authSlice';
import { Button, Input, Card } from '../../components/ui/UIComponents';

const LoginPage = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector(state => state.auth);
  
  const handleSubmit = async (values) => {
    try {
      await dispatch(loginUser(values)).unwrap();
      navigate('/admin/dashboard');
    } catch (err) {
      // Error is handled by the authSlice
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
            Sign in to access the document generator
          </Typography.Text>
        </div>
        
        {error && (
          <Alert
            message="Authentication Error"
            description={error}
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
            label="Username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input placeholder="Username" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full"
              icon={<LoginOutlined />}
              loading={loading}
            >
              Sign In
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage; 