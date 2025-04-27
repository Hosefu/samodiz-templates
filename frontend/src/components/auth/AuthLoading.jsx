import React from 'react';
import { Loader2 } from 'lucide-react';
import * as text from '../../constants/ux-writing';

const AuthLoading = () => {
  return (
    <div className="flex items-center justify-center">
      <Loader2 className="animate-spin h-5 w-5 text-blue-600" />
      <span className="ml-3 text-sm text-gray-700">{text.AUTH_LOADING}</span>
    </div>
  );
};

export default AuthLoading; 