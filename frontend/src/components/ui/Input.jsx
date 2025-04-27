import React from 'react';

const Input = ({ 
  label, 
  name, 
  value, 
  onChange, 
  required = false, 
  type = 'text', 
  placeholder = '',
  error,
  hint
}) => (
  <div className="mb-4">
    {label && (
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
    )}
    <input
      type={type}
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      required={required}
      placeholder={placeholder}
      className={`w-full px-3 py-2 border ${error ? 'border-red-500' : 'border-gray-300'} rounded-md focus:outline-none focus:ring-2 ${error ? 'focus:ring-red-500' : 'focus:ring-blue-500'} focus:border-transparent`}
      aria-invalid={error ? "true" : "false"}
      aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
    />
    {hint && !error && <p className="mt-1 text-xs text-gray-500" id={`${name}-hint`}>{hint}</p>}
    {error && <p className="mt-1 text-xs text-red-600" id={`${name}-error`}>{error}</p>}
  </div>
);

export default Input; 