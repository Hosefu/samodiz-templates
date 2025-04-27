import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isAuthenticated: false,
  user: null,
  tokens: null,
  loading: false,
  error: null
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.loading = false;
      state.error = null;
    },
    loginFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.tokens = null;
      state.loading = false;
      state.error = null;
    },
    updateTokens: (state, action) => {
      state.tokens = action.payload;
    }
  }
});

export const { loginStart, loginSuccess, loginFailure, logout, updateTokens } = authSlice.actions;
export default authSlice.reducer; 