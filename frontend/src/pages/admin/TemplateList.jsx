import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTemplates } from '../../context/TemplateContext';
import { deleteTemplate } from '../../api/templateService';
import * as text from '../../constants/ux-writing';
import Button from '../../components/ui/Button';
import { Loader2, FilePlus, Edit, Trash2, AlertCircle } from 'lucide-react';
import Modal from '../../components/ui/Modal';

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
        <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
        <span className="ml-2 text-gray-600">{text.ADMIN_TEMPLATE_LIST_LOADING}</span>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 bg-red-100 p-4 rounded-md">{text.ADMIN_TEMPLATE_LIST_ERROR(error)}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-800">{text.ADMIN_TEMPLATE_LIST_TITLE}</h1>
        <Link to="/admin/templates/new">
           <Button variant="default" icon={<FilePlus />}>
             {text.ADMIN_TEMPLATE_LIST_CREATE_BUTTON}
           </Button>
        </Link>
      </div>

      {templates.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow border border-gray-200">
          <p className="text-gray-500">{text.ADMIN_TEMPLATE_LIST_NO_TEMPLATES}</p>
          <Link to="/admin/templates/new" className="mt-4 inline-block">
            <Button variant="default" icon={<FilePlus />}>
               {text.ADMIN_TEMPLATE_LIST_CREATE_BUTTON}
            </Button>
           </Link>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_NAME}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_VERSION}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_TYPE}
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_PAGES}
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {text.ADMIN_TEMPLATE_LIST_TABLE_HEADER_ACTIONS}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {templates.map((template) => (
                <tr key={template.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{template.name || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{template.version || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {template.type ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {template.type.toUpperCase()}
                      </span>
                    ) : (
                       <span className="text-gray-400 text-xs">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                    {template.pages?.length ?? 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <Link 
                      to={`/admin/templates/${template.id}`}
                      className="text-blue-600 hover:text-blue-800"
                      title={text.ADMIN_TEMPLATE_LIST_EDIT_BUTTON}
                    >
                       <Button variant="ghost" size="sm" icon={<Edit />} />
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Trash2 className="text-red-600" />} 
                      onClick={() => openDeleteConfirm(template)}
                      title={text.ADMIN_TEMPLATE_LIST_DELETE_BUTTON}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <Modal 
        isOpen={showDeleteConfirm}
        onClose={closeDeleteConfirm}
        title={text.ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_TITLE}
      >
        <div className="space-y-4">
           <div className="flex items-start space-x-3">
                <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0"/>
                <p className="text-sm text-gray-600">
                    {text.ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_MSG(templateToDelete?.name || '')}
                </p>
           </div>
           {deleteError && (
              <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{deleteError}</p>
           )}
           <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <Button variant="outline" onClick={closeDeleteConfirm} disabled={isDeleting}>
                    {text.ADMIN_TEMPLATE_LIST_CANCEL_BUTTON}
                </Button>
                <Button variant="danger" onClick={handleDelete} isLoading={isDeleting}>
                    {text.ADMIN_TEMPLATE_LIST_DELETE_BUTTON}
                </Button>
           </div>
        </div>
      </Modal>
    </div>
  );
};

export default TemplateList; 