import React from 'react';

const Card = ({ children, title, className = '', titleRight }) => (
  <div className={`bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden ${className}`}>
    {title && (
      <div className="flex justify-between items-center border-b border-gray-200 p-4">
        <h3 className="font-semibold text-gray-800 text-lg">{title}</h3>
        {titleRight && <div>{titleRight}</div>}
      </div>
    )}
    <div className="p-6">
      {children}
    </div>
  </div>
);

export default Card; 