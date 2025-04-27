import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  theme: 'dark',
  sidebarCollapsed: false,
  notifications: [],
  modals: {
    isOpen: false,
    type: null,
    data: null
  }
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    addNotification: (state, action) => {
      state.notifications.push(action.payload);
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    openModal: (state, action) => {
      state.modals = {
        isOpen: true,
        type: action.payload.type,
        data: action.payload.data
      };
    },
    closeModal: (state) => {
      state.modals = {
        isOpen: false,
        type: null,
        data: null
      };
    }
  }
});

export const { 
  setTheme, 
  toggleSidebar, 
  addNotification, 
  removeNotification,
  openModal,
  closeModal
} = uiSlice.actions;

export default uiSlice.reducer; 