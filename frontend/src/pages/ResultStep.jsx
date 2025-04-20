import React from 'react';
import { Button, Card } from '../components/ui';
import { useFormContext } from '../context/FormContext';
import { useTemplateContext } from '../context/TemplateContext';
import { Download, RefreshCw } from 'lucide-react';

const ResultStep = ({ onBack, onNewDocument }) => {
  const { generatedDoc } = useFormContext();
  const { selectedTemplate } = useTemplateContext();

  if (!generatedDoc || !selectedTemplate) {
    return (
      <Card>
        <div className="text-center py-4">
          Документ не сгенерирован. <button className="text-blue-500" onClick={onBack}>Вернуться назад</button>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Документ успешно сгенерирован">
      <div className="space-y-6">
        <div className="text-center">
          <div className="text-xl font-medium mb-2">{selectedTemplate.name}</div>
          <p className="text-slate-600 mb-4">Документ готов к скачиванию</p>
          
          {generatedDoc.previewUrl && (
            <div className="border rounded-lg overflow-hidden mb-6 max-w-xl mx-auto">
              <iframe 
                src={generatedDoc.previewUrl} 
                className="w-full h-96" 
                title="Document Preview"
              />
            </div>
          )}
          
          <div className="flex flex-col sm:flex-row justify-center gap-4 mt-6">
            <Button
              onClick={() => window.open(generatedDoc.url, '_blank')}
              icon={<Download className="h-4 w-4" />}
            >
              Скачать документ
            </Button>
            
            <Button 
              variant="secondary" 
              onClick={onNewDocument}
              icon={<RefreshCw className="h-4 w-4" />}
            >
              Создать новый документ
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ResultStep; 