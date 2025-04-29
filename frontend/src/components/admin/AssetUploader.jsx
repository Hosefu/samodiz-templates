import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { uploadAsset } from '../../api/assetService';
import * as text from '../../constants/ux-writing';
import { toast } from 'react-hot-toast';

const AssetUploader = ({ templateId, pageId, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);

  const uploadProps = {
    name: 'file',
    multiple: false,
    beforeUpload: (file) => {
      // Log file information for debugging
      console.log('Before upload file:', file.name, file.type, file.size);
      return true; // Return true to continue with upload
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      if (!file) {
        console.error('No file provided to customRequest');
        message.error('Файл не выбран');
        onError(new Error('No file provided'));
        return;
      }
      
      console.log('Starting upload of file:', file.name, file.type, file.size);
      
      try {
        setUploading(true);
        // Pass the file directly, not wrapped in an event
        const response = await uploadAsset(templateId, pageId, file);
        
        console.log('Upload successful, response:', response);
        onSuccess();
        toast.success(`Файл "${file.name}" успешно загружен`);
        
        if (onUploadSuccess && response) {
          onUploadSuccess(response);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        onError(error);
        toast.error(error.message || 'Ошибка загрузки файла');
      } finally {
        setUploading(false);
      }
    },
    onError: (error) => {
      console.error('Upload component error:', error);
    },
    onDrop(e) {
      console.log('Dropped files:', e.dataTransfer.files);
    },
  };

  return (
    <div className="asset-uploader">
      <Upload {...uploadProps} disabled={uploading}>
        <Button icon={<UploadOutlined />} loading={uploading}>
          {uploading ? 'Загрузка...' : 'Загрузить ассет'}
        </Button>
      </Upload>
      <div className="mt-2 text-sm text-gray-500">
        Поддерживаемые форматы: PNG, JPG, GIF, SVG, PDF, TTF, OTF (макс. 10MB)
      </div>
    </div>
  );
};

export default AssetUploader; 