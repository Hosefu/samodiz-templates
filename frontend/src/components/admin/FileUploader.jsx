import React, { useState, useRef } from 'react';

const FileUploader = ({ onFileUpload, templateId, pageId }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    try {
      setUploading(true);
      await onFileUpload(templateId, pageId, file);
      // Reset the input
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setUploading(false);
    }
  };

  const onButtonClick = () => {
    inputRef.current.click();
  };

  return (
    <div 
      className={`p-6 border-2 border-dashed rounded-lg text-center ${
        dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        id="file-upload"
        onChange={handleChange}
        className="hidden"
      />
      
      <svg 
        className="mx-auto h-12 w-12 text-gray-400" 
        stroke="currentColor" 
        fill="none" 
        viewBox="0 0 48 48" 
        aria-hidden="true"
      >
        <path 
          d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
          strokeWidth={2} 
          strokeLinecap="round" 
          strokeLinejoin="round" 
        />
      </svg>
      
      <div className="flex text-sm text-gray-600 justify-center mt-2">
        <label
          htmlFor="file-upload"
          className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500"
        >
          <span onClick={onButtonClick}>Upload a file</span>
        </label>
        <p className="pl-1">or drag and drop</p>
      </div>
      
      <p className="text-xs text-gray-500 mt-1">
        PNG, JPG, GIF, SVG, TTF, OTF up to 10MB
      </p>

      {uploading && (
        <div className="mt-3">
          <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-blue-500 border-r-transparent"></div>
          <span className="ml-2 text-sm text-gray-600">Uploading...</span>
        </div>
      )}
    </div>
  );
};

export default FileUploader; 