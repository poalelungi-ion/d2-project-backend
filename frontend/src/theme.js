import { createTheme } from '@mui/material/styles';

/**
 * Generates a consistent glassmorphism theme across the application.
 * Adapts dynamically to light/dark mode toggles.
 */
export const getGlassTheme = (mode) => createTheme({
  palette: {
    mode,
    primary: { main: mode === 'light' ? '#B71C1C' : '#ef4444' }, // Red accent
    secondary: { main: mode === 'light' ? '#424242' : '#9ca3af' }, 
    background: { default: 'transparent', paper: mode === 'light' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(45, 45, 45, 0.85)' },
    text: { primary: mode === 'light' ? '#212121' : '#f3f4f6', secondary: mode === 'light' ? 'text.secondary' : '#9ca3af' }
  },
  shape: { borderRadius: 16 },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: mode === 'light' ? '1px solid rgba(255, 255, 255, 0.6)' : '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: mode === 'light' ? '0 8px 32px 0 rgba(31, 38, 135, 0.1)' : '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
          backgroundImage: 'none',
          transition: 'all 0.3s ease',
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          '&:hover': {
             transform: 'translateY(-2px)',
             boxShadow: mode === 'light' ? '0 12px 40px 0 rgba(0, 0, 0, 0.1)' : '0 12px 40px 0 rgba(0,0,0,0.6)',
          }
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          overflow: 'hidden'
        }
      }
    }
  }
});
