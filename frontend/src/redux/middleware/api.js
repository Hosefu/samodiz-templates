import { createAsyncThunk } from '@reduxjs/toolkit';

export const apiMiddleware = store => next => action => {
  // Логируем все API-запросы
  if (action.type?.startsWith('api/')) {
    console.log('API Request:', action);
  }
  
  // Обрабатываем ошибки API
  if (action.type?.endsWith('/rejected')) {
    console.error('API Error:', action.payload);
  }
  
  return next(action);
};

// Хелпер для создания асинхронных действий с обработкой ошибок
export const createApiAction = (type, apiCall) => {
  return createAsyncThunk(
    type,
    async (params, { rejectWithValue }) => {
      try {
        const response = await apiCall(params);
        return response;
      } catch (error) {
        return rejectWithValue(error.message || 'Произошла ошибка при выполнении запроса');
      }
    }
  );
}; 