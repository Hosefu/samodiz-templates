import React from 'react';

const Card = ({ children, title, className = '' }) => (
  <div className={`bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden ${className}`}>
    {title && (
      <div className="border-b border-slate-200 p-4 font-medium">
        {title}
      </div>
    )}
    <div className="p-4">
      {children}
    </div>
  </div>
);

export default Card; 