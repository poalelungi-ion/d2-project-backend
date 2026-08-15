import React, { useState, useEffect } from 'react';
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
import { StudentDetail } from './StudentDetail';

export const StudentsAdmin = (props) => {
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
  
    if (selectedStudent) {
      return <StudentDetail {...props} />;
    }

    let activeStudents = studentsData;
    if (studentSearchQuery) {
      activeStudents = activeStudents.filter(s => 
        s.name.toLowerCase().includes(studentSearchQuery.toLowerCase()) || 
        s.student_id.toString().includes(studentSearchQuery)
      );
    }

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
             <Box>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>LSF Student Roster</Typography>
                <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400' }}>Manage the student directory and view individual marks.</Typography>
             </Box>
             <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <ToggleButtonGroup 
                  value={studentViewMode} 
                  exclusive 
                  onChange={(e, v) => v && setStudentViewMode(v)} 
                  size="small"
                  sx={{ bgcolor: 'background.paper', borderRadius: '12px' }}
                >
                  <ToggleButton value="grid">Grid</ToggleButton>
                  <ToggleButton value="table">Table</ToggleButton>
                </ToggleButtonGroup>
                
                <TextField 
                  size="small" 
                  placeholder="Search students..." 
                  value={studentSearchQuery}
                  onChange={(e) => setStudentSearchQuery(e.target.value)}
                  sx={{ bgcolor: 'background.paper', borderRadius: '12px', '& .MuiOutlinedInput-root': { borderRadius: '12px' } }}
                />
                
                <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => openStudentForm()} sx={{ borderRadius: '12px', height: 48, px: 3, boxShadow: '0 8px 20px rgba(183, 28, 28, 0.3)' }}>Add Student</Button>
             </Box>
          </Box>
          
          {studentViewMode === 'grid' ? (
            <Grid container spacing={3}>
              {activeStudents.map(student => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={student.student_id}>
                  <Card sx={{ cursor: 'pointer', border: student.program === 'Unknown' ? '2px solid #FF8F00' : 'none', position: 'relative' }} onClick={() => fetchStudentTranscript(student.student_id)}>
                    <Box sx={{ position: 'absolute', top: 12, right: 12, zIndex: 2 }}>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); openStudentForm(student); }}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    {student.program === 'Unknown' && (
                       <Box sx={{ position: 'absolute', top: 12, left: 12, color: '#FF8F00' }}>
                          <WarningAmberIcon />
                       </Box>
                    )}
                    <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Avatar sx={{ width: 72, height: 72, bgcolor: '#424242', fontSize: '2rem', fontWeight: 'bold', mb: 2, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                        {student.name.charAt(0)}
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: '700', textAlign: 'center' }}>{student.name}</Typography>
                      <Typography variant="body2" sx={{ color: '#B71C1C', mb: 2, fontWeight: '600' }}>{student.student_id}</Typography>
                      <Divider sx={{ width: '100%', mb: 2, opacity: 0.5 }} />
                      <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', px: 1 }}>
                         <Typography variant="body2" sx={{color: 'text.secondary'}}>Exams: <strong>{student.total_exams}</strong></Typography>
                         <Typography variant="body2" sx={{color: 'text.secondary'}}>Avg: <strong>{student.avg_grade}</strong></Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <div className="ag-theme-alpine" style={{ flex: 1, width: '100%', height: '600px', marginTop: '16px' }}>
              <AgGridReact 
                rowData={activeStudents} 
                columnDefs={studentRosterColumnDefs} 
                defaultColDef={{ resizable: true, sortable: true, filter: true }} 
                animateRows={true}
                pagination={true}
                paginationPageSize={20}
                onRowClicked={(e) => fetchStudentTranscript(e.data.student_id)}
              />
            </div>
          )}
        </Box>
      </Fade>
    );
  };

