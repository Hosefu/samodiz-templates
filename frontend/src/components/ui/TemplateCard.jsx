import React from 'react';
import { CheckCircle, FileText } from 'lucide-react'; // Импортируем иконку для типа
import * as text from '../../constants/ux-writing'; // Добавляем импорт констант

const TemplateCard = ({ template, selected, onClick }) => (
  <div
    className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ease-in-out transform hover:-translate-y-1 hover:shadow-lg ${selected ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 bg-white hover:border-blue-300'}`}
    onClick={onClick}
    role="button"
    aria-pressed={selected}
    tabIndex={0} // Делаем карточку доступной для фокуса
    onKeyPress={(e) => (e.key === 'Enter' || e.key === ' ') && onClick()} // Обработка нажатия клавиш
  >
    <div className="flex justify-between items-start"> {/* Изменяем alignment */}
      <div className="flex-1 mr-4"> {/* Добавляем отступ */}
        <h3 className="font-semibold text-gray-800 mb-1">{template.name || text.TEMPLATE_NAME_DEFAULT}</h3> {/* Используем константу */}
        <p className="text-sm text-gray-500 mb-2">{text.HOME_TEMPLATE_VERSION} {template.version || 'N/A'}</p> {/* Используем константу */}
        <div className="flex items-center text-xs text-gray-600">
          <FileText className="h-4 w-4 mr-1 text-gray-400" />
          <span>{template.pages ? text.HOME_TEMPLATE_PAGES_COUNT(template.pages.length) : text.HOME_TEMPLATE_NO_PAGES}</span> {/* Используем константу */}
          {template.type && (
             <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
               {template.type.toUpperCase()}
             </span>
          )}
        </div>
      </div>
      {selected && (
        <div className="flex-shrink-0">
            <CheckCircle className="text-blue-600 h-6 w-6" />
        </div>
      )}
    </div>
  </div>
);

export default TemplateCard; 