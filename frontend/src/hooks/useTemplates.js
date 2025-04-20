import { useState, useEffect } from 'react';

export const useTemplates = () => {
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('/api/templates/');
      if (!response.ok) {
        throw new Error('Не удалось загрузить шаблоны');
      }
      const data = await response.json();
      setTemplates(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  return { templates, isLoading, error, fetchTemplates };
}; 