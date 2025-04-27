import React from 'react';
import Editor from '@monaco-editor/react';
import { Card } from 'antd';

const CodeEditor = ({ value, onChange, language = 'html', height = '400px' }) => {
  const handleEditorChange = (value) => {
    onChange(value);
  };

  // Настройка темы для Monaco Editor (тёмная)
  const editorOptions = {
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    fontSize: 14,
    tabSize: 2,
    wordWrap: 'on',
    lineNumbers: 'on',
    automaticLayout: true,
    theme: 'vs-dark'
  };

  return (
    <div style={{ 
      border: '1px solid #303030', 
      borderRadius: '2px',
      overflow: 'hidden'
    }}>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        options={editorOptions}
      />
    </div>
  );
};

export default CodeEditor; 