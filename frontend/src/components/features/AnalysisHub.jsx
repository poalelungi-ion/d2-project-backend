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

export const AnalysisHub = (props) => {
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
  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px', color: '#212121' }}>Welcome back, Professor Adam! 👋</Typography>
        <Typography variant="h6" sx={{ mb: 4, color: 'text.secondary', fontWeight: '400' }}>Here are your actionable insights for active cohorts.</Typography>
        
        <Grid container spacing={4} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'rgba(25, 118, 210, 0.05)', border: '1px solid rgba(25, 118, 210, 0.2)' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" fontWeight="600">Active Enrolled Students</Typography>
                <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: '#1976D2' }}>{stats.kpis?.total_active_students || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'rgba(46, 125, 50, 0.05)', border: '1px solid rgba(46, 125, 50, 0.2)' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" fontWeight="600">University Pass Rate</Typography>
                <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: '#2E7D32' }}>{stats.kpis?.active_pass_rate || 0}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'rgba(255, 143, 0, 0.05)', border: '1px solid rgba(255, 143, 0, 0.2)' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" fontWeight="600">Average Active Grade</Typography>
                <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: '#FF8F00' }}>{stats.kpis?.active_avg_grade || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'rgba(158, 158, 158, 0.05)', border: '1px solid rgba(158, 158, 158, 0.2)' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" fontWeight="600">Archived Courses</Typography>
                <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: '#757575' }}>{stats.kpis?.total_archived_courses || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 4, height: '100%' }}>
                <Typography variant="h5" sx={{ fontWeight: '700', mb: 3 }}>Toughest Courses (Lowest Pass Rates)</Typography>
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>Identify which active courses are causing the most failures.</Typography>
                <Box sx={{ height: 320 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stats.toughest_courses} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="rgba(0,0,0,0.1)"/>
                      <XAxis type="number" domain={[0, 100]} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="course_name" width={200} axisLine={false} tickLine={false} style={{ fontSize: '0.85rem' }} />
                      <RechartsTooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{ borderRadius: '16px', border: '1px solid rgba(255,255,255,0.5)', boxShadow: '0 8px 32px rgba(0,0,0,0.1)', backdropFilter: 'blur(20px)' }} />
                      <Bar dataKey="pass_rate" fill="#D32F2F" radius={[0, 6, 6, 0]} name="Pass Rate (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

};
