/**
 * @file App.jsx
 * @description Main React application component for the SPA System.
 * Handles routing (simulated via steps), global state management, file uploads,
 * data validation, and visual analytics dashboards.
 */
import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, LineChart, Line } from 'recharts';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  Box, Drawer, AppBar, CssBaseline, Toolbar, List, Typography, Divider, 
  ListItem, ListItemButton, ListItemIcon, ListItemText, Button, Paper, Grid, Card, CardContent, Snackbar, Alert, Fade, Avatar,
  FormControl, InputLabel, Select, MenuItem, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tabs, Tab, Pagination, Skeleton, ToggleButton, ToggleButtonGroup, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Stepper, Step, StepLabel, Badge
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import TableChartIcon from '@mui/icons-material/TableChart';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AssessmentIcon from '@mui/icons-material/Assessment';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import DownloadIcon from '@mui/icons-material/Download';
import SaveIcon from '@mui/icons-material/Save';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import EmailIcon from '@mui/icons-material/Email';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import ArchiveIcon from '@mui/icons-material/Archive';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';
import RestoreIcon from '@mui/icons-material/Restore';

const drawerWidth = 260;

import { getGlassTheme } from './theme';
import { useAppLogic } from './hooks/useAppLogic.jsx';
import { CourseFormDialog } from './components/forms/CourseFormDialog.jsx';
import { StudentFormDialog } from './components/forms/StudentFormDialog.jsx';
import { AddGradeDialog } from './components/forms/AddGradeDialog.jsx';

import { AnalysisHub } from './components/features/AnalysisHub.jsx';
import { BatchUploadWizard } from './components/features/BatchUploadWizard.jsx';
import { CourseDetail } from './components/features/CourseDetail.jsx';
import { CoursesAdmin } from './components/features/CoursesAdmin.jsx';
import { StudentDetail } from './components/features/StudentDetail.jsx';
import { StudentsAdmin } from './components/features/StudentsAdmin.jsx';
import { SystemLogs } from './components/features/SystemLogs.jsx';

export default function App() {
  const appState = useAppLogic();
  const { activeTab, setActiveTab, setSelectedStudent, setSelectedCourse, themeMode, toggleTheme, toast, setToast } = appState;
  const glassTheme = React.useMemo(() => getGlassTheme(themeMode), [themeMode]);

  const menuItems = [
    { text: 'Teacher Dashboard', icon: <DashboardIcon /> },
    { text: 'Batch Data Upload', icon: <TableChartIcon /> },
    { text: 'Analysis Hub', icon: <SchoolIcon /> },
    { text: 'Student LSF Roster', icon: <PersonIcon /> },
  ];

  return (
    <ThemeProvider theme={glassTheme}>

      

      <Box sx={{ display: 'flex', height: '100vh', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
        <CssBaseline />
        <AppBar position="fixed" elevation={0} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, background: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255, 255, 255, 0.5)', color: '#212121' }}>
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: '800', background: 'linear-gradient(45deg, #B71C1C 30%, #FF8E53 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Study Progress Analysis
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary' }}>Software Systems Engineering</Typography>
          </Toolbar>
        </AppBar>
        
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', background: 'rgba(255, 255, 255, 0.6)', backdropFilter: 'blur(40px)', borderRight: '1px solid rgba(255, 255, 255, 0.8)' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2, px: 2 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton 
                    selected={activeTab === item.text}
                    onClick={() => { setActiveTab(item.text); setSelectedStudent(null); setSelectedCourse(null); }}
                    sx={{
                      borderRadius: '12px',
                      '&.Mui-selected': { background: 'linear-gradient(135deg, rgba(183, 28, 28, 0.1), rgba(183, 28, 28, 0.05))', color: '#B71C1C' },
                      '&:hover': { background: 'rgba(255, 255, 255, 0.9)' }
                    }}
                  >
                    <ListItemIcon sx={{ color: activeTab === item.text ? '#B71C1C' : 'inherit' }}>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} sx={{ '& .MuiTypography-root': { fontWeight: activeTab === item.text ? 700 : 500 } }} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
        
        
      <CourseFormDialog {...appState} />
      <StudentFormDialog {...appState} />
      <AddGradeDialog {...appState} />

      <Box component="main" sx={{ flexGrow: 1, p: 4, pt: 10, overflowY: 'auto' }}>
          
          
          {activeTab === 'Teacher Dashboard' && <AnalysisHub {...appState} />}
          {activeTab === 'Batch Data Upload' && <BatchUploadWizard {...appState} />}
          {activeTab === 'Analysis Hub' && <CoursesAdmin {...appState} />}
          {activeTab === 'Student LSF Roster' && <StudentsAdmin {...appState} />}
        </Box>
      </Box>
      
      


      
      
      <Snackbar open={toast.open} autoHideDuration={6000} onClose={() => setToast({...toast, open: false})}>
        <Alert severity={toast.severity} sx={{ width: '100%', borderRadius: '16px', backdropFilter: 'blur(20px)', background: toast.severity === 'success' ? 'rgba(46, 125, 50, 0.9)' : 'rgba(211, 47, 47, 0.9)', color: '#FFF' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}
