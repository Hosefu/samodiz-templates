import React from 'react';
import Editor from '@monaco-editor/react';

const CodeEditor = ({ value, onChange, language = 'html', height = '400px' }) => {
  const handleEditorChange = (value) => {
    onChange(value);
  };

  return (
    <div 
      style={{ 
        border: '1px solid #e2e8f0', 
        borderRadius: '0.375rem',
        overflow: 'hidden'
      }}
    >
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        options={{
          minimap: { enabled: true },
          scrollBeyondLastLine: false,
          fontSize: 14,
          tabSize: 2,
          wordWrap: 'on',
          lineNumbers: 'on',
          automaticLayout: true,
        }}
      />
    </div>
  );
};

export default CodeEditor; 