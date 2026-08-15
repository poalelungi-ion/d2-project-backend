import React, { useRef, useState, useEffect } from 'react';
import { Restore as RestoreIcon } from '@mui/icons-material';
import { Divider } from '@mui/material';
import { ChevronLeft as ChevronLeftIcon } from '@mui/icons-material';
import { Cancel as CancelIcon } from '@mui/icons-material';
import { AgGridReact } from 'ag-grid-react';
import { 
  Box, Typography, Grid, Card, CardContent, Button, TextField, 
  Stepper, Step, StepLabel, Select, MenuItem, FormControl, InputLabel,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  LinearProgress, Fade, Collapse, Alert, Avatar, Tooltip, Tab, Tabs
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  UploadFile as UploadFileIcon, CheckCircle as CheckCircleIcon,
  Warning as WarningIcon, Error as ErrorIcon, Delete as DeleteIcon,
  Edit as EditIcon, Add as AddIcon, Refresh as RefreshIcon,
  MoreVert as MoreVertIcon, School as SchoolIcon, Assessment as AssessmentIcon,
  Timeline as TimelineIcon, Save as SaveIcon, Close as CloseIcon,
  ArrowBack as ArrowBackIcon, Check as CheckIcon,
  Dashboard as DashboardIcon, TableChart as TableChartIcon, Person as PersonIcon,
  History as HistoryIcon, ExpandMore as ExpandMoreIcon, WarningAmber as WarningAmberIcon
} from '@mui/icons-material';
import { TABS, STEPS } from '../../utils/constants';

export const StudentDetail = (props) => {
  const { 
        themeMode, setThemeMode, activeTab, setActiveTab, coursesData, setCoursesData,
    studentsData, setStudentsData, selectedStudent, setSelectedStudent, selectedCourse,
    setSelectedCourse, analyticsStudent, setAnalyticsStudent, analyticsStudentTranscript,
    setAnalyticsStudentTranscript, courseFormOpen, setCourseFormOpen, courseFormMode,
    setCourseFormMode, courseForm, setCourseForm, courseFormErrors, setCourseFormErrors,
    editCourseVersion, setEditCourseVersion, addGradeDialogOpen, setAddGradeDialogOpen,
    addGradeForm, setAddGradeForm, archiveTab, setArchiveTab, newCourseName,
    setNewCourseName, uploadForm, setUploadForm, previewData, setPreviewData,
    gridApi, setGridApi, uploadPreview, setUploadPreview, activeStep, setActiveStep,
    selectedDemoFile, setSelectedDemoFile, uploadCourseInfo, setUploadCourseInfo,
    nameSplitRule, setNameSplitRule, stats, setStats, toast, setToast, loadingCourses,
    setLoadingCourses, coursesSortBy, setCoursesSortBy, studentViewMode, setStudentViewMode,
    studentSearchQuery, setStudentSearchQuery, studentFormOpen, setStudentFormOpen,
    studentFormMode, setStudentFormMode, studentForm, setStudentForm, studentFormErrors,
    setStudentFormErrors, editStudentVersion, setEditStudentVersion, searchQuery,
    setSearchQuery, coursesPage, setCoursesPage, viewMode, setViewMode, newCourseId,
    setNewCourseId, studentColumnDefs,
    toggleTheme, fetchData, fetchStudentTranscript, saveGradesToDB, openCourseForm, 
    openStudentForm, validateStudentForm, handleSaveStudent, validateCourseForm, 
    handleSaveCourse, handleUploadSubmit, updateStudentProgram, handleArchiveCourse, 
    handleStudentStatus, handleAddGrade, handleUpload, handleConfirmUpload
  } = props;
  const studentGridRef = useRef(null);
  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ mb: 3 }}>
          <Button startIcon={<ChevronLeftIcon />} onClick={() => setSelectedStudent(null)} sx={{ color: '#424242', mb: 1 }}>Return to List</Button>
          <Typography variant="h3" sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>{selectedStudent.name}</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1, flexWrap: 'wrap' }}>
            <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400' }}>ID: {selectedStudent.student_id}</Typography>
            <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
            <TextField 
              size="small" 
              label="Learning Program" 
              value={selectedStudent.program} 
              onChange={(e) => setSelectedStudent({...selectedStudent, program: e.target.value})}
              sx={{ width: 250 }}
              error={selectedStudent.program === 'Unknown'}
              helperText={selectedStudent.program === 'Unknown' ? "Action required: Update program" : ""}
            />
            <Button variant="contained" size="small" onClick={updateStudentProgram} sx={{ borderRadius: '8px' }}>Save Profile</Button>
            {selectedStudent.status === 'active' && (
              <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
                 <Button variant="outlined" color="success" startIcon={<CheckCircleIcon />} onClick={() => handleStudentStatus(selectedStudent.student_id, 'graduated')} sx={{ borderRadius: '8px' }}>Graduate</Button>
                 <Button variant="outlined" color="error" startIcon={<CancelIcon />} onClick={() => handleStudentStatus(selectedStudent.student_id, 'failed')} sx={{ borderRadius: '8px' }}>Fail Student</Button>
              </Box>
            )}
            {selectedStudent.status !== 'active' && (
              <Box sx={{ ml: 'auto', display: 'flex', gap: 2, alignItems: 'center' }}>
                 <Typography variant="h6" color={selectedStudent.status === 'graduated' ? 'success.main' : 'error.main'} sx={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                    Status: {selectedStudent.status}
                 </Typography>
                 <Button variant="outlined" color="primary" startIcon={<RestoreIcon />} onClick={() => handleStudentStatus(selectedStudent.student_id, 'active')} sx={{ borderRadius: '8px' }}>Restore to Active</Button>
              </Box>
            )}
          </Box>
        </Box>
        
        <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: '24px', overflow: 'hidden' }}>
          <Box sx={{ p: 3, borderBottom: '1px solid rgba(0, 0, 0, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" fontWeight="700">Personal Transcript</Typography>
              <Typography variant="body1" color="text.secondary">View and edit marks directly in the student's official record grid.</Typography>
            </Box>
            <Box sx={{ display: 'flex' }}>
              <Button variant="outlined" color="primary" startIcon={<AddIcon />} onClick={() => setAddGradeDialogOpen(true)} sx={{ px: 3, mr: 2, borderRadius: '8px' }}>
                Add Course Record
              </Button>
              <Button variant="contained" color="primary" startIcon={<SaveIcon />} onClick={() => saveGradesToDB(studentGridRef)} sx={{ px: 3 }}>
                Save Official Marks
              </Button>
            </Box>
          </Box>
          <div className="ag-theme-alpine" style={{ flex: 1, width: '100%', padding: '16px' }}>
            <AgGridReact 
              ref={studentGridRef} 
              rowData={selectedStudent.transcript} 
              columnDefs={studentColumnDefs} 
              defaultColDef={{ resizable: true, sortable: true, filter: true }} 
              animateRows={true} 
              pagination={true}
              paginationPageSize={20}
            />
          </div>
        </Paper>
      </Box>
    </Fade>
  );

};
