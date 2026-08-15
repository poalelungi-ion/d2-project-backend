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

export const CoursesAdmin = (props) => {
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
    handleTabChange, fetchStats, fetchStudents, fetchCourses, uploadDemoFile, handleUploadNext,
    handleUploadBack, confirmUpload, resetUploadForm, fetchCourseDetails, handleCourseSave,
    handleCourseDelete, handleCourseArchiveToggle, handleStudentSave, handleStudentStatusChange,
    handleStudentDelete, fetchStudentDetails, handleAddGrade, handleDemoSelection,
    fetchDashboardAnalytics, fetchStudentAnalytics, theme, drawerWidth
  } = props;
  
    if (selectedCourse) {
      return renderCourseDetail();
    }

    let activeCourses = coursesData.filter(c => !c.is_archived);
    if (searchQuery) {
      activeCourses = activeCourses.filter(c => 
        c.course_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        c.course_id.toString().includes(searchQuery)
      );
    }
    if (coursesSortBy === 'name') {
      activeCourses.sort((a, b) => a.course_name.localeCompare(b.course_name));
    } else if (coursesSortBy === 'semester') {
      activeCourses.sort((a, b) => (a.semester || '').localeCompare(b.semester || ''));
    }

    const itemsPerPage = 20;
    const pageCount = Math.ceil(activeCourses.length / itemsPerPage);
    const paginatedCourses = activeCourses.slice((coursesPage - 1) * itemsPerPage, coursesPage * itemsPerPage);

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
             <Box>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px', m: 0 }}>Analysis Hub</Typography>
                <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400', mt: 1 }}>Select a course to view detailed analytics.</Typography>
             </Box>
             <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <ToggleButtonGroup 
                  value={viewMode} 
                  exclusive 
                  onChange={(e, newMode) => { if(newMode) setViewMode(newMode); }} 
                  size="small"
                  sx={{ bgcolor: 'background.paper' }}
                >
                  <ToggleButton value="grid">Grid</ToggleButton>
                  <ToggleButton value="table">Table</ToggleButton>
                </ToggleButtonGroup>
                
                <TextField 
                  size="small" 
                  placeholder="Search courses..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ bgcolor: 'background.paper', borderRadius: '12px', '& .MuiOutlinedInput-root': { borderRadius: '12px' } }}
                />
                {viewMode === 'grid' && (
                  <FormControl size="small" sx={{ minWidth: 200, bgcolor: 'background.paper', borderRadius: '12px' }}>
                    <InputLabel>Sort By</InputLabel>
                    <Select value={coursesSortBy} label="Sort By" onChange={(e) => setCoursesSortBy(e.target.value)} sx={{ borderRadius: '12px' }}>
                      <MenuItem value="name">Course Name (A-Z)</MenuItem>
                      <MenuItem value="semester">Semester (Chronological)</MenuItem>
                    </Select>
                  </FormControl>
                )}
                <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => openCourseForm()} sx={{ borderRadius: '12px', height: 48, px: 3, boxShadow: '0 8px 20px rgba(183, 28, 28, 0.3)' }}>Create New Course</Button>
             </Box>
          </Box>
          
          {loadingCourses ? (
            <Grid container spacing={3}>
               {[1, 2, 3, 4, 5, 6].map(i => (
                 <Grid item xs={12} md={6} lg={4} key={i}>
                   <Skeleton variant="rectangular" height={200} sx={{ borderRadius: '12px' }} />
                 </Grid>
               ))}
            </Grid>
          ) : activeCourses.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 10 }}>
               <Typography variant="h5" color="text.secondary">No courses are currently available.</Typography>
            </Box>
          ) : (
            <>
              {viewMode === 'grid' ? (
                <Grid container spacing={3}>
                  {paginatedCourses.map(course => (
                    <Grid item xs={12} md={6} lg={4} key={course.course_id}>
                      <Card sx={{ cursor: 'pointer', transition: 'all 0.2s', '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 12px 24px rgba(0,0,0,0.1)' } }} onClick={() => setSelectedCourse(course)}>
                        <CardContent sx={{ p: 3, position: "relative" }}>
                          <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
                            <IconButton size="small" onClick={(e) => { e.stopPropagation(); openCourseForm(course); }}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Box>

                          <Typography variant="h6" sx={{ fontWeight: '700', mb: 1.5, mt: 0.5 }}>{course.course_name}</Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2, gap: 1, flexWrap: 'wrap' }}>
                             <Typography variant="caption" sx={{ color: 'text.secondary', bgcolor: 'rgba(0,0,0,0.05)', px: 1, py: 0.5, borderRadius: 1 }}>{course.semester}</Typography>
                             <Typography variant="caption" sx={{ color: 'text.secondary', bgcolor: 'rgba(0,0,0,0.05)', px: 1, py: 0.5, borderRadius: 1 }}>ID: {course.course_id}</Typography>
                             <Typography variant="caption" sx={{ color: 'text.secondary', bgcolor: 'rgba(0,0,0,0.05)', px: 1, py: 0.5, borderRadius: 1 }}>{course.assigned_professor}</Typography>
                          </Box>
                          <Divider sx={{ mb: 2, opacity: 0.5 }} />
                          <Typography variant="body2" sx={{display: 'flex', justifyContent: 'space-between', mb: 1}}>
                            Submissions: <strong>{course.total_attempts}</strong>
                          </Typography>
                          <Typography variant="body2" sx={{display: 'flex', justifyContent: 'space-between', mb: 1}}>
                            Pass Rate: <strong style={{color: course.pass_rate > 50 ? '#2E7D32' : '#D32F2F'}}>{course.pass_rate}%</strong>
                          </Typography>
                          <Typography variant="body2" sx={{display: 'flex', justifyContent: 'space-between'}}>
                            Avg Grade: <strong>{course.avg_grade}</strong>
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <div className="ag-theme-alpine" style={{ flex: 1, width: '100%', height: '600px', marginTop: '16px' }}>
                  <AgGridReact 
                    rowData={activeCourses} 
                    columnDefs={courseColumnDefs} 
                    defaultColDef={{ resizable: true, sortable: true, filter: true }} 
                    animateRows={true}
                    pagination={true}
                    paginationPageSize={20}
                    onRowClicked={(e) => setSelectedCourse(e.data)}
                  />
                </div>
              )}
            </>
          )}
        </Box>
      </Fade>
    );
  };

