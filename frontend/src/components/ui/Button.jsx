import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = ({ 
  children, 
  variant = 'default', 
  size = 'default', 
  disabled = false, 
  onClick, 
  className = '', 
  icon,
  isLoading = false,
  type = 'button'
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variantClasses = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50',
    secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
    ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
    link: 'text-blue-600 underline-offset-4 hover:underline',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  
  const sizeClasses = {
    default: 'h-10 py-2 px-4 text-sm',
    sm: 'h-8 px-3 text-xs',
    lg: 'h-12 px-8 text-base',
    icon: 'h-10 w-10',
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  return (
    <button 
      className={classes} 
      disabled={disabled || isLoading} 
      onClick={onClick}
      type={type}
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : icon ? (
        <span className="mr-2 -ml-1 h-5 w-5">{React.cloneElement(icon, { className: "h-4 w-4" })}</span>
      ) : null}
      {children}
    </button>
  );
};

export default Button; 