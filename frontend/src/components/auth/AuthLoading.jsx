import React from 'react';

const AuthLoading = () => {
  return (
    <div className="flex justify-center items-center py-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <span className="ml-3 text-sm text-gray-700">Загрузка...</span>
    </div>
  );
};

export default AuthLoading; 