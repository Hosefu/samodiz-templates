import React, { useState } from 'react';
import { Card, Tabs } from 'antd';
import AssetUploader from './AssetUploader';
import AssetList from './AssetList';

const AssetManager = ({ templateId, pageId, assets = [], onAssetsChange }) => {
  const [activeTab, setActiveTab] = useState('upload');

  const handleUploadSuccess = (newAsset) => {
    if (onAssetsChange) {
      onAssetsChange([...assets, newAsset]);
    }
  };

  const handleAssetDeleted = (deletedAssetId) => {
    if (onAssetsChange) {
      onAssetsChange(assets.filter(asset => asset.id !== deletedAssetId));
    }
  };

  return (
    <Card title="Управление файлами">
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'upload',
            label: 'Загрузка файлов',
            children: (
              <AssetUploader
                templateId={templateId}
                pageId={pageId}
                onUploadSuccess={handleUploadSuccess}
              />
            )
          },
          {
            key: 'list',
            label: 'Список файлов',
            children: (
              <AssetList
                templateId={templateId}
                pageId={pageId}
                assets={assets}
                onAssetDeleted={handleAssetDeleted}
              />
            )
          }
        ]}
      />
    </Card>
  );
};

export default AssetManager; 