import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { uploadAsset } from '../../api/assetService';

const AssetUploader = ({ templateId, pageId, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file) => {
    setUploading(true);
    try {
      const response = await uploadAsset(templateId, pageId, file);
      message.success(`${file.name} успешно загружен`);
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
      return true;
    } catch (error) {
      // Отображаем сообщение об ошибке из валидации или API
      message.error(error.message || 'Ошибка при загрузке файла');
      return false;
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    showUploadList: true,
    beforeUpload: async (file) => {
      const result = await handleUpload(file);
      return false; // Предотвращаем автоматическую загрузку
    },
    disabled: uploading,
  };

  return (
    <Upload {...uploadProps}>
      <Button 
        icon={<UploadOutlined />} 
        loading={uploading}
        disabled={uploading}
      >
        {uploading ? 'Загрузка...' : 'Загрузить файл'}
      </Button>
      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
        Поддерживаемые форматы: JPG, PNG, GIF, SVG, PDF
        <br />
        Максимальный размер: 10MB
      </div>
    </Upload>
  );
};

export default AssetUploader; 