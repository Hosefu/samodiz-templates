import React, { useState } from 'react';
import { Tabs } from 'antd';
import AssetUploader from './AssetUploader';
import AssetList from './AssetList';
import * as text from '../../constants/ux-writing';
import { Card } from '../ui/UIComponents';
import { UploadIcon, ImageIcon } from 'lucide-react';

const AssetManager = ({ templateId, pageId, assets = [], onAssetsChange }) => {
  const [activeTab, setActiveTab] = useState('upload');

  const handleUploadSuccess = (newAsset) => {
    console.log('Asset uploaded successfully:', newAsset);
    if (onAssetsChange) {
      onAssetsChange([...assets, newAsset]);
    }
  };

  const handleAssetDeleted = (deletedAssetId) => {
    console.log('Asset deleted:', deletedAssetId);
    if (onAssetsChange) {
      onAssetsChange(assets.filter(asset => asset.id !== deletedAssetId));
    }
  };

  const items = [
    {
      key: 'upload',
      label: (
        <div className="flex items-center gap-2">
          <UploadIcon size={16} />
          <span>Загрузить файлы</span>
        </div>
      ),
      children: (
        <div className="py-4">
          <AssetUploader
            templateId={templateId}
            pageId={pageId}
            onUploadSuccess={handleUploadSuccess}
          />
        </div>
      )
    },
    {
      key: 'list',
      label: (
        <div className="flex items-center gap-2">
          <ImageIcon size={16} />
          <span>Список файлов{assets.length > 0 ? ` (${assets.length})` : ''}</span>
        </div>
      ),
      children: (
        <div className="py-2">
          <AssetList
            templateId={templateId}
            pageId={pageId}
            assets={assets}
            onAssetDeleted={handleAssetDeleted}
          />
        </div>
      )
    }
  ];

  return (
    <div>
      <Tabs 
        activeKey={activeTab}
        onChange={setActiveTab}
        items={items}
      />
    </div>
  );
};

export default AssetManager; 