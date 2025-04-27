import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchTemplates, fetchTemplateById, updateTemplate, createTemplate, deleteTemplate } from '../../api/templateService';

export const fetchAllTemplates = createAsyncThunk(
  'templates/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await fetchTemplates();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchTemplate = createAsyncThunk(
  'templates/fetchOne',
  async (id, { rejectWithValue }) => {
    try {
      return await fetchTemplateById(id);
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateTemplateAction = createAsyncThunk(
  'templates/update',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      return await updateTemplate(id, data);
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const createTemplateAction = createAsyncThunk(
  'templates/create',
  async (data, { rejectWithValue }) => {
    try {
      return await createTemplate(data);
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const deleteTemplateAction = createAsyncThunk(
  'templates/delete',
  async (id, { rejectWithValue }) => {
    try {
      await deleteTemplate(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  templates: [],
  currentTemplate: null,
  loading: false,
  error: null
};

const templateSlice = createSlice({
  name: 'templates',
  initialState,
  reducers: {
    clearCurrentTemplate: (state) => {
      state.currentTemplate = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch all templates
      .addCase(fetchAllTemplates.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAllTemplates.fulfilled, (state, action) => {
        state.templates = action.payload;
        state.loading = false;
      })
      .addCase(fetchAllTemplates.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch single template
      .addCase(fetchTemplate.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTemplate.fulfilled, (state, action) => {
        state.currentTemplate = action.payload;
        state.loading = false;
      })
      .addCase(fetchTemplate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update template
      .addCase(updateTemplateAction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateTemplateAction.fulfilled, (state, action) => {
        state.currentTemplate = action.payload;
        state.templates = state.templates.map(template => 
          template.id === action.payload.id ? action.payload : template
        );
        state.loading = false;
      })
      .addCase(updateTemplateAction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create template
      .addCase(createTemplateAction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createTemplateAction.fulfilled, (state, action) => {
        state.templates.push(action.payload);
        state.loading = false;
      })
      .addCase(createTemplateAction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Delete template
      .addCase(deleteTemplateAction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteTemplateAction.fulfilled, (state, action) => {
        state.templates = state.templates.filter(template => template.id !== action.payload);
        state.loading = false;
      })
      .addCase(deleteTemplateAction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearCurrentTemplate, clearError } = templateSlice.actions;
export default templateSlice.reducer; 