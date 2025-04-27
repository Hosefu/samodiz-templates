import React from 'react';

const Checkbox = ({ label, id, name, checked, onChange, error, hint, className = '' }) => (
  <div className={`flex items-start ${className}`}>
    <div className="flex items-center h-5">
      <input
        id={id}
        name={name || id} // Используем id, если name не предоставлен
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className={`focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded ${error ? 'border-red-500' : ''}`}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
      />
    </div>
    <div className="ml-2 text-sm">
      {label && (
         <label htmlFor={id} className="font-medium text-gray-700 cursor-pointer">
           {label}
         </label>
      )}
      {hint && !error && <p className="text-xs text-gray-500" id={`${id}-hint`}>{hint}</p>}
      {error && <p className="text-xs text-red-600" id={`${id}-error`}>{error}</p>}
    </div>
  </div>
);

export default Checkbox; 