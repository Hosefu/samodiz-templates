import { Button as AntButton, Input as AntInput, Select as AntSelect, 
  Checkbox as AntCheckbox, Card as AntCard, Modal as AntModal, 
  Spin, Form, Upload, message, Alert, Space, Typography, Table, Tag } from 'antd';
import { 
  SaveOutlined, PlusOutlined, DeleteOutlined, 
  UploadOutlined, CopyOutlined, LoadingOutlined 
} from '@ant-design/icons';

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
    <AntButton 
      type={typeMap[variant] || 'primary'}
      danger={variant === 'danger'}
      loading={isLoading}
      icon={icon} 
      {...props}
    >
      {children}
    </AntButton>
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
      <AntInput {...props} />
    </Form.Item>
  );
};

// Select компонент
export const Select = ({ label, options, error, hint, ...props }) => {
  return (
    <Form.Item 
      label={label} 
      validateStatus={error ? 'error' : ''}
      help={error || hint}
    >
      <AntSelect
        {...props}
        options={options}
      />
    </Form.Item>
  );
};

// Checkbox с label
export const Checkbox = ({ label, ...props }) => {
  return <AntCheckbox {...props}>{label}</AntCheckbox>;
};

// Card компонент
export const Card = ({ title, children, titleRight, ...props }) => {
  return (
    <AntCard 
      title={title} 
      extra={titleRight} 
      {...props}
    >
      {children}
    </AntCard>
  );
};

// Modal компонент
export const Modal = ({ isOpen, onClose, title, children, ...props }) => {
  return (
    <AntModal
      open={isOpen}
      onCancel={onClose}
      title={title}
      footer={null}
      {...props}
    >
      {children}
    </AntModal>
  );
};

// Также экспортируем иконки для удобства
export const Icons = {
  Save: SaveOutlined,
  Plus: PlusOutlined,
  Delete: DeleteOutlined,
  Upload: UploadOutlined,
  Copy: CopyOutlined,
  Loading: LoadingOutlined
};

// Экспортируем оригинальные компоненты Ant Design
export { Form, Upload, message, Spin, Alert, Space, Typography, Table, Tag }; 