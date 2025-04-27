import React, { useState } from 'react';
import { Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';

const { Dragger } = Upload;

const FileUploader = ({ onFileUpload, templateId, pageId }) => {
  const [uploading, setUploading] = useState(false);

  const uploadProps = {
    name: 'file',
    multiple: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        setUploading(true);
        await onFileUpload(templateId, pageId, file);
        onSuccess();
        message.success(`${file.name} успешно загружен`);
      } catch (error) {
        console.error('Error uploading file:', error);
        onError();
        message.error(`Ошибка загрузки ${file.name}`);
      } finally {
        setUploading(false);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  return (
    <Dragger {...uploadProps} disabled={uploading}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">Нажмите или перетащите файл в эту область для загрузки</p>
      <p className="ant-upload-hint">
        Поддерживаются файлы PNG, JPG, GIF, SVG, TTF, OTF до 10MB
      </p>
    </Dragger>
  );
};

export default FileUploader; 