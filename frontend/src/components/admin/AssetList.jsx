import React, { useState } from 'react';
import { List, Image as AntImage, Modal as AntModal, Empty } from 'antd';
import { deleteAsset } from '../../api/assetService';
import { toast } from 'react-hot-toast';
import * as text from '../../constants/ux-writing';
import { Button } from '../ui/UIComponents';
import { Trash2, Eye, Copy, ExternalLink, ImageIcon, FileIcon } from 'lucide-react';

const AssetList = ({ templateId, pageId, assets = [], onAssetDeleted }) => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [previewTitle, setPreviewTitle] = useState('');
  const [deletingAssetId, setDeletingAssetId] = useState(null);

  const handleDelete = async (assetId) => {
    try {
      setDeletingAssetId(assetId);
      await deleteAsset(templateId, pageId, assetId);
      toast.success('Ассет успешно удален');
      if (onAssetDeleted) {
        onAssetDeleted(assetId);
      }
    } catch (error) {
      console.error('Error deleting asset:', error);
      toast.error(`Ошибка удаления ассета: ${error.message || 'Неизвестная ошибка'}`);
    } finally {
      setDeletingAssetId(null);
    }
  };

  const handlePreview = (asset) => {
    // Only preview images
    if (asset.file_type && asset.file_type.startsWith('image/')) {
      setPreviewImage(asset.url || `/api/templates/${templateId}/pages/${pageId}/assets/${asset.id}/`);
      setPreviewTitle(asset.name || 'Предпросмотр изображения');
      setPreviewVisible(true);
    } else {
      // For non-image files, open in a new tab
      window.open(asset.url || `/api/templates/${templateId}/pages/${pageId}/assets/${asset.id}/`, '_blank');
    }
  };

  const copyAssetUrl = (asset) => {
    const url = asset.url || `/api/templates/${templateId}/pages/${pageId}/assets/${asset.id}/`;
    navigator.clipboard.writeText(url)
      .then(() => toast.success('URL скопирован в буфер обмена'))
      .catch(err => toast.error('Не удалось скопировать URL'));
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Неизвестно';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (fileType) => {
    if (!fileType) return <FileIcon size={24} className="text-gray-400" />;
    if (fileType.startsWith('image/')) return <ImageIcon size={24} className="text-blue-500" />;
    return <FileIcon size={24} className="text-gray-400" />;
  };

  if (!assets || assets.length === 0) {
    return (
      <Empty 
        description="Нет загруженных файлов" 
        image={Empty.PRESENTED_IMAGE_SIMPLE} 
      />
    );
  }

  return (
    <>
      <List
        itemLayout="horizontal"
        dataSource={assets}
        renderItem={(asset) => (
          <List.Item
            className="py-3 hover:bg-gray-50 transition-colors"
            actions={[
              <Button
                key="preview"
                variant="ghost" 
                size="sm"
                onClick={() => handlePreview(asset)}
                title="Просмотр файла"
                icon={<Eye size={16} />}
              />,
              <Button
                key="copy"
                variant="ghost" 
                size="sm"
                onClick={() => copyAssetUrl(asset)}
                title="Скопировать URL"
                icon={<Copy size={16} />}
              />,
              <Button
                key="open"
                variant="ghost" 
                size="sm"
                onClick={() => window.open(asset.url || `/api/templates/${templateId}/pages/${pageId}/assets/${asset.id}/`, '_blank')}
                title="Открыть в новой вкладке"
                icon={<ExternalLink size={16} />}
              />,
              <Button
                key="delete"
                variant="ghost" 
                size="sm"
                isLoading={deletingAssetId === asset.id}
                onClick={() => handleDelete(asset.id)}
                title="Удалить файл"
                icon={deletingAssetId === asset.id ? null : <Trash2 size={16} className="text-red-500" />}
              />
            ]}
          >
            <List.Item.Meta
              avatar={getFileIcon(asset.file_type)}
              title={
                <div className="font-medium">{asset.name || asset.file || 'Безымянный файл'}</div>
              }
              description={
                <div className="text-xs text-gray-500">
                  {asset.file_type && <span className="mr-3">Тип: {asset.file_type}</span>}
                  {asset.size && <span>Размер: {formatFileSize(asset.size)}</span>}
                </div>
              }
            />
          </List.Item>
        )}
      />

      <AntModal
        open={previewVisible}
        title={previewTitle}
        footer={null}
        onCancel={() => setPreviewVisible(false)}
      >
        <AntImage
          alt={previewTitle}
          style={{ width: '100%' }}
          src={previewImage}
        />
      </AntModal>
    </>
  );
};

export default AssetList; 