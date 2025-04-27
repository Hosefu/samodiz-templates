import React, { useState } from 'react';
import { List, Button, Image, Modal } from 'antd';
import { DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { deleteAsset, getAssetUrl } from '../../api/assetService';
import { toast } from 'react-hot-toast';
import * as text from '../../constants/ux-writing';

const AssetList = ({ templateId, pageId, assets, onAssetDeleted }) => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState('');

  const handleDelete = async (assetId) => {
    try {
      await deleteAsset(templateId, pageId, assetId);
      toast.success(text.ASSET_LIST_DELETE_SUCCESS);
      if (onAssetDeleted) {
        onAssetDeleted(assetId);
      }
    } catch (error) {
      toast.error(text.ASSET_LIST_DELETE_ERROR(error.message));
    }
  };

  const handlePreview = (asset) => {
    setPreviewImage(getAssetUrl(templateId, pageId, asset.id));
    setPreviewVisible(true);
  };

  return (
    <>
      <List
        itemLayout="horizontal"
        dataSource={assets}
        renderItem={(asset) => (
          <List.Item
            actions={[
              <Button
                key="preview"
                type="text"
                icon={<EyeOutlined />}
                onClick={() => handlePreview(asset)}
              >
                {text.ASSET_LIST_PREVIEW_BUTTON}
              </Button>,
              <Button
                key="delete"
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(asset.id)}
              >
                {text.ASSET_LIST_DELETE_BUTTON}
              </Button>
            ]}
          >
            <List.Item.Meta
              title={asset.name}
              description={`${text.ASSET_LIST_TYPE_LABEL} ${asset.type}, ${text.ASSET_LIST_SIZE_LABEL} ${(asset.size / 1024).toFixed(2)} KB`}
            />
          </List.Item>
        )}
      />

      <Modal
        open={previewVisible}
        title={text.ASSET_LIST_PREVIEW_TITLE}
        footer={null}
        onCancel={() => setPreviewVisible(false)}
      >
        <Image
          alt="preview"
          style={{ width: '100%' }}
          src={previewImage}
        />
      </Modal>
    </>
  );
};

export default AssetList; 