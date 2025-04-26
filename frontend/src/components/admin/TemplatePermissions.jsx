import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TemplatePermissions = ({ templateId }) => {
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Форма для нового разрешения
  const [formData, setFormData] = useState({
    permission_type: 'view',
    user: '',
    group: ''
  });

  // Загрузка данных при монтировании компонента
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [permissionsResponse, usersResponse, groupsResponse] = await Promise.all([
          axios.get(`/api/templates/${templateId}/permissions/`),
          axios.get('/api/users/'),
          axios.get('/api/groups/')
        ]);
        
        setPermissions(permissionsResponse.data);
        setUsers(usersResponse.data);
        setGroups(groupsResponse.data);
      } catch (err) {
        console.error('Error loading permissions data:', err);
        setError('Failed to load permissions data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [templateId]);

  // Обработка изменения формы
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Если выбран пользователь, очищаем группу и наоборот
    if (name === 'user' && value) {
      setFormData({ ...formData, user: value, group: '' });
    } else if (name === 'group' && value) {
      setFormData({ ...formData, group: value, user: '' });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  // Добавление нового разрешения
  const handleAddPermission = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post(`/api/templates/${templateId}/add_permission/`, formData);
      setPermissions([...permissions, response.data]);
      
      // Сброс формы
      setFormData({
        permission_type: 'view',
        user: '',
        group: ''
      });
    } catch (err) {
      console.error('Error adding permission:', err);
      setError('Failed to add permission');
    }
  };

  // Удаление разрешения
  const handleDeletePermission = async (permissionId) => {
    if (!window.confirm('Are you sure you want to delete this permission?')) return;
    
    try {
      await axios.delete(`/api/templates/${templateId}/remove_permission/${permissionId}/`);
      setPermissions(permissions.filter(p => p.id !== permissionId));
    } catch (err) {
      console.error('Error deleting permission:', err);
      setError('Failed to delete permission');
    }
  };

  if (loading) return <div>Loading permissions...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="bg-white shadow overflow-hidden rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Template Permissions</h3>
        
        {/* Список существующих разрешений */}
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-500">Current Permissions</h4>
          
          {permissions.length === 0 ? (
            <p className="mt-2 text-sm text-gray-500">No custom permissions set for this template.</p>
          ) : (
            <div className="mt-2 space-y-2">
              {permissions.map(permission => (
                <div key={permission.id} className="flex justify-between items-center py-2 border-b">
                  <div>
                    {permission.user_details ? (
                      <span className="font-medium">User: {permission.user_details.username}</span>
                    ) : (
                      <span className="font-medium">Group: {permission.group_details.name}</span>
                    )}
                    <span className="ml-2 text-sm text-gray-500">
                      ({permission.permission_type})
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeletePermission(permission.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Форма добавления нового разрешения */}
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-500">Add Permission</h4>
          
          <form onSubmit={handleAddPermission} className="mt-2">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-sm font-medium text-gray-700">Permission Type</label>
                <select
                  name="permission_type"
                  value={formData.permission_type}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="view">View</option>
                  <option value="edit">Edit</option>
                  <option value="generate">Generate</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">User</label>
                <select
                  name="user"
                  value={formData.user}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Select a user</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.username}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Group</label>
                <select
                  name="group"
                  value={formData.group}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  disabled={!!formData.user}
                >
                  <option value="">Select a group</option>
                  {groups.map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="mt-4">
              <button
                type="submit"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                disabled={(!formData.user && !formData.group)}
              >
                Add Permission
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TemplatePermissions; 