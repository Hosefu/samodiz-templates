import React from 'react';
import { Button as AntButton, Input as AntInput, Select as AntSelect, 
  Checkbox as AntCheckbox, Card as AntCard, Form } from 'antd';
import styled from 'styled-components';

// Стилизованные компоненты в стиле Krea.ai

const StyledButton = styled(AntButton)`
  &.ant-btn-primary {
    background-color: #3B82F6;
    border-color: #3B82F6;
    &:hover {
      background-color: #2563EB;
      border-color: #2563EB;
    }
  }
  
  &.ant-btn-default {
    background-color: #262626;
    border-color: #333333;
    color: #D1D5DB;
    &:hover {
      background-color: #333333;
      border-color: #4B4B4B;
    }
  }
  
  &.ant-btn-link {
    color: #3B82F6;
    &:hover {
      color: #2563EB;
    }
  }
  
  &.ant-btn-text {
    color: #D1D5DB;
    &:hover {
      background-color: rgba(255, 255, 255, 0.08);
    }
  }
  
  &.ant-btn-dangerous {
    color: #EF4444;
    border-color: #EF4444;
    &.ant-btn-primary {
      background-color: #EF4444;
      color: white;
    }
  }
`;

const StyledCard = styled(AntCard)`
  background-color: #1F1F1F;
  border-color: #2C2C2C;
  
  .ant-card-head {
    background-color: #262626;
    border-color: #2C2C2C;
    color: #F5F5F5;
  }
  
  .ant-card-body {
    background-color: #1F1F1F;
    color: #D1D5DB;
  }
`;

const StyledInput = styled(AntInput)`
  background-color: #262626;
  border-color: #333333;
  color: #D1D5DB;
  
  &:hover {
    border-color: #3B82F6;
  }
  
  &:focus, &-focused {
    border-color: #3B82F6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  
  &::placeholder {
    color: #6B7280;
  }
`;

const StyledPassword = styled(AntInput.Password)`
  background-color: #262626;
  border-color: #333333;
  color: #D1D5DB;
  
  &:hover {
    border-color: #3B82F6;
  }
  
  &:focus, &-focused {
    border-color: #3B82F6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  
  &::placeholder {
    color: #6B7280;
  }
  
  .ant-input {
    background-color: #262626;
    color: #D1D5DB;
  }
  
  .ant-input-password-icon {
    color: #6B7280;
    &:hover {
      color: #3B82F6;
    }
  }
`;

const StyledSelect = styled(AntSelect)`
  .ant-select-selector {
    background-color: #262626 !important;
    border-color: #333333 !important;
    color: #D1D5DB !important;
  }
  
  .ant-select-selection-item {
    color: #D1D5DB !important;
  }
  
  &:hover .ant-select-selector {
    border-color: #3B82F6 !important;
  }
  
  &.ant-select-focused .ant-select-selector {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
  }
`;

// Кнопка с иконкой
export const Button = ({ children, icon, isLoading, variant = 'primary', ...props }) => {
  // Маппинг для типов кнопок
  const typeMap = {
    'primary': 'primary',
    'outline': 'default',
    'danger': 'primary',
    'secondary': 'default',
    'ghost': 'text'
  };
  
  return (
    <StyledButton 
      type={typeMap[variant] || 'primary'}
      danger={variant === 'danger'}
      loading={isLoading}
      icon={icon} 
      {...props}
    >
      {children}
    </StyledButton>
  );
};

// Input с поддержкой label и error
export const Input = ({ label, error, hint, ...props }) => {
  return (
    <Form.Item 
      label={label} 
      validateStatus={error ? 'error' : ''}
      help={error || hint}
    >
      <StyledInput {...props} />
    </Form.Item>
  );
};

// Password Input компонент
export const PasswordInput = ({ label, error, hint, ...props }) => {
  return (
    <Form.Item 
      label={label} 
      validateStatus={error ? 'error' : ''}
      help={error || hint}
    >
      <StyledPassword {...props} />
    </Form.Item>
  );
};

// Добавим поддержку Input.Password
Input.Password = (props) => <StyledPassword {...props} />;

// Select компонент
export const Select = ({ label, options, error, hint, ...props }) => {
  return (
    <Form.Item 
      label={label} 
      validateStatus={error ? 'error' : ''}
      help={error || hint}
    >
      <StyledSelect
        {...props}
        options={options}
      />
    </Form.Item>
  );
};

// Checkbox с label
export const Checkbox = ({ label, ...props }) => {
  return (
    <AntCheckbox 
      {...props}
      style={{ color: '#D1D5DB' }}
    >
      {label}
    </AntCheckbox>
  );
};

// Card компонент
export const Card = ({ title, children, titleRight, ...props }) => {
  return (
    <StyledCard 
      title={title} 
      extra={titleRight} 
      {...props}
    >
      {children}
    </StyledCard>
  );
};

export { Form }; 