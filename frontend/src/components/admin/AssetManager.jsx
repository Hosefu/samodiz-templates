import React, { useState } from 'react';
import { Card, Tabs } from 'antd';
import AssetUploader from './AssetUploader';
import AssetList from './AssetList';
import * as text from '../../constants/ux-writing';

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
    <Card title={text.ASSET_MANAGER_TITLE}>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'upload',
            label: text.ASSET_MANAGER_UPLOAD_TAB,
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
            label: text.ASSET_MANAGER_LIST_TAB,
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