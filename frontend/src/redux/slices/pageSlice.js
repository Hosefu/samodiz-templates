import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { createPage as apiCreatePage, updatePage as apiUpdatePage, deletePage as apiDeletePage } from '../../api/pageService';

export const createPage = createAsyncThunk(
  'pages/create',
  async ({ templateId, pageData }, { rejectWithValue }) => {
    try {
      return await apiCreatePage(templateId, pageData);
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to create page');
    }
  }
);

export const updatePage = createAsyncThunk(
  'pages/update',
  async ({ templateId, pageId, pageData }, { rejectWithValue }) => {
    try {
      return await apiUpdatePage(templateId, pageId, pageData);
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to update page');
    }
  }
);

export const deletePage = createAsyncThunk(
  'pages/delete',
  async ({ templateId, pageId }, { rejectWithValue }) => {
    try {
      await apiDeletePage(templateId, pageId);
      return { templateId, pageId };
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to delete page');
    }
  }
);

const initialState = {
  currentPage: null,
  loading: false,
  error: null
};

const pageSlice = createSlice({
  name: 'pages',
  initialState,
  reducers: {
    clearCurrentPage: (state) => {
      state.currentPage = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Create page
      .addCase(createPage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createPage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPage = action.payload;
      })
      .addCase(createPage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Update page
      .addCase(updatePage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updatePage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPage = action.payload;
      })
      .addCase(updatePage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Delete page
      .addCase(deletePage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deletePage.fulfilled, (state) => {
        state.loading = false;
        state.currentPage = null;
      })
      .addCase(deletePage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearCurrentPage, clearError } = pageSlice.actions;
export default pageSlice.reducer; 