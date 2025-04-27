import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { uploadAsset } from '../../api/assetService';

const AssetUploader = ({ templateId, pageId, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);

  const uploadProps = {
    name: 'file',
    multiple: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      if (!file) {
        message.error('No file selected');
        return;
      }
      
      try {
        setUploading(true);
        const response = await uploadAsset(templateId, pageId, file);
        onSuccess();
        message.success(`${file.name} uploaded successfully`);
        if (onUploadSuccess) {
          onUploadSuccess(response);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        onError();
        message.error(error.message || 'Failed to upload file');
      } finally {
        setUploading(false);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  return (
    <Upload {...uploadProps} disabled={uploading}>
      <Button icon={<UploadOutlined />} loading={uploading}>
        {uploading ? 'Uploading...' : 'Upload Asset'}
      </Button>
      <div className="mt-2 text-sm text-gray-400">
        Supported formats: PNG, JPG, GIF, SVG, TTF, OTF (max 10MB)
      </div>
    </Upload>
  );
};

export default AssetUploader; 