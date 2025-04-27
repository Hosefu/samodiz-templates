import React, { useState } from 'react';
import { Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import * as text from '../../constants/ux-writing';

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
        message.success(text.FILE_UPLOAD_SUCCESS(file.name));
      } catch (error) {
        console.error('Error uploading file:', error);
        onError();
        message.error(text.FILE_UPLOAD_ERROR(file.name));
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
      <p className="ant-upload-text">{text.FILE_UPLOAD_DRAG_TEXT}</p>
      <p className="ant-upload-hint">
        {text.FILE_UPLOAD_HINT}
      </p>
    </Dragger>
  );
};

export default FileUploader; 