import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTemplates } from '../../context/TemplateContext';
import { deleteTemplate } from '../../api/templateService';
import * as text from '../../constants/ux-writing';
import { 
  Button, Card, Space, Typography, Spin, Alert, Table, Tag, Modal 
} from '../../components/ui/AntComponents';
import { 
  FileAddOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined 
} from '@ant-design/icons';

const TemplateList = () => {
  const { templates, loading, error, refreshTemplates } = useTemplates();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const openDeleteConfirm = (template) => {
    setTemplateToDelete(template);
    setShowDeleteConfirm(true);
    setDeleteError(null);
  };

  const closeDeleteConfirm = () => {
    setShowDeleteConfirm(false);
    setTemplateToDelete(null);
  };

  const handleDelete = async () => {
    if (!templateToDelete) return;
    
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteTemplate(templateToDelete.id);
      refreshTemplates();
      closeDeleteConfirm();
    } catch (err) {
      console.error('Failed to delete template:', err);
      setDeleteError(err.message || 'Не удалось удалить шаблон.'); 
    } finally {
      setIsDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Spin size="large" />
        <span className="ml-2 text-gray-600">{text.ADMIN_TEMPLATE_LIST_LOADING}</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Ошибка"
        description={text.ADMIN_TEMPLATE_LIST_ERROR(error)}
        type="error"
        showIcon
      />
    );
  }

  const columns = [
    {
      title: text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_NAME,
      dataIndex: 'name',
      key: 'name',
      render: (text) => text || '-'
    },
    {
      title: text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_VERSION,
      dataIndex: 'version',
      key: 'version',
      render: (text) => text || '-'
    },
    {
      title: text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_TYPE,
      dataIndex: 'type',
      key: 'type',
      render: (type) => type ? (
        <Tag color="blue">{type.toUpperCase()}</Tag>
      ) : (
        <span className="text-gray-400">N/A</span>
      )
    },
    {
      title: text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_PAGES,
      dataIndex: 'pages',
      key: 'pages',
      align: 'center',
      render: (pages) => pages?.length ?? 0
    },
    {
      title: text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_ACTIONS,
      key: 'actions',
      align: 'right',
      render: (_, record) => (
        <Space>
          <Link to={`/admin/templates/${record.id}`}>
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              title={text.ADMIN_TEMPLATE_LIST_EDIT_BUTTON}
            />
          </Link>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => openDeleteConfirm(record)}
            title={text.ADMIN_TEMPLATE_LIST_DELETE_BUTTON}
          />
        </Space>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <Typography.Title level={2}>
          {text.ADMIN_TEMPLATE_LIST_TITLE}
        </Typography.Title>
        <Link to="/admin/templates/new">
          <Button type="primary" icon={<FileAddOutlined />}>
            {text.ADMIN_TEMPLATE_LIST_CREATE_BUTTON}
          </Button>
        </Link>
      </div>

      {templates.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Typography.Text type="secondary">
              {text.ADMIN_TEMPLATE_LIST_NO_TEMPLATES}
            </Typography.Text>
            <div className="mt-4">
              <Link to="/admin/templates/new">
                <Button type="primary" icon={<FileAddOutlined />}>
                  {text.ADMIN_TEMPLATE_LIST_CREATE_BUTTON}
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      ) : (
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="id"
          pagination={false}
        />
      )}
      
      <Modal
        title={text.ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_TITLE}
        open={showDeleteConfirm}
        onCancel={closeDeleteConfirm}
        footer={[
          <Button key="cancel" onClick={closeDeleteConfirm} disabled={isDeleting}>
            {text.ADMIN_TEMPLATE_LIST_CANCEL_BUTTON}
          </Button>,
          <Button 
            key="delete" 
            type="primary" 
            danger 
            onClick={handleDelete} 
            loading={isDeleting}
          >
            {text.ADMIN_TEMPLATE_LIST_DELETE_BUTTON}
          </Button>
        ]}
      >
        <Space>
          <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
          <Typography.Text>
            {text.ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_MSG(templateToDelete?.name || '')}
          </Typography.Text>
        </Space>
        {deleteError && (
          <Alert
            message={deleteError}
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Modal>
    </div>
  );
};

export default TemplateList; 