import { ThemeConfig } from 'antd';

export const lightTheme: ThemeConfig = {
  token: {
    colorPrimary: '#6366F1', // Indigo 500
    colorSuccess: '#22C55E', // Green 500
    colorWarning: '#F59E0B', // Amber 500
    colorError: '#EF4444',   // Red 500
    colorInfo: '#3B82F6',    // Blue 500
    borderRadius: 8,
    fontSize: 14,
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      bodyBg: '#f9fafb',
      siderBg: '#ffffff',
    },
    Button: {
      controlHeight: 40,
      borderRadius: 8,
    },
    Input: {
      controlHeight: 40,
      borderRadius: 8,
    },
  },
};

export const darkTheme: ThemeConfig = {
  token: {
    colorPrimary: '#6366F1',
    colorSuccess: '#22C55E',
    colorWarning: '#F59E0B',
    colorError: '#EF4444',
    colorInfo: '#3B82F6',
    borderRadius: 8,
    fontSize: 14,
    colorBgBase: '#1f2937',
    colorTextBase: '#f9fafb',
  },
  components: {
    Layout: {
      headerBg: '#111827',
      bodyBg: '#1f2937',
      siderBg: '#111827',
    },
  },
};

