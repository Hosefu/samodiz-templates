import React, { useState } from 'react';
import { List, Button, Image, Modal } from 'antd';
import { DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { deleteAsset, getAssetUrl } from '../../api/assetService';
import { toast } from 'react-hot-toast';

const AssetList = ({ templateId, pageId, assets, onAssetDeleted }) => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState('');

  const handleDelete = async (assetId) => {
    try {
      await deleteAsset(templateId, pageId, assetId);
      toast.success('Файл успешно удален');
      if (onAssetDeleted) {
        onAssetDeleted(assetId);
      }
    } catch (error) {
      toast.error(`Ошибка удаления файла: ${error.message}`);
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
                Просмотр
              </Button>,
              <Button
                key="delete"
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(asset.id)}
              >
                Удалить
              </Button>
            ]}
          >
            <List.Item.Meta
              title={asset.name}
              description={`Тип: ${asset.type}, Размер: ${(asset.size / 1024).toFixed(2)} KB`}
            />
          </List.Item>
        )}
      />

      <Modal
        open={previewVisible}
        title="Предпросмотр файла"
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