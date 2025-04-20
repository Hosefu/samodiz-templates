import React from 'react';
import { CheckCircle } from 'lucide-react';

const TemplateCard = ({ template, selected, onClick }) => (
  <div 
    className={`border rounded-lg p-4 cursor-pointer transition-colors ${selected ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-blue-300'}`}
    onClick={onClick}
  >
    <div className="flex justify-between items-center">
      <div>
        <h3 className="font-medium text-slate-900">{template.name}</h3>
        <p className="text-sm text-slate-500">Версия: {template.version}</p>
        <div className="flex items-center mt-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {template.type.toUpperCase()}
          </span>
          <span className="ml-2 text-xs text-slate-500">{template.pages.length} страниц</span>
        </div>
      </div>
      {selected && (
        <CheckCircle className="text-blue-500 h-6 w-6" />
      )}
    </div>
  </div>
);

export default TemplateCard; 