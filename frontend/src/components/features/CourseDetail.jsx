import React, { useRef, useState, useEffect } from 'react';
import { Legend } from 'recharts';
import { Restore as RestoreIcon } from '@mui/icons-material';
import { ChevronLeft as ChevronLeftIcon } from '@mui/icons-material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { AgGridReact } from 'ag-grid-react';
import { Archive as ArchiveIcon } from '@mui/icons-material';
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

export const CourseDetail = (props) => {
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
  const courseGridRef = useRef(null);

  const getGradeDistributionData = () => {
    if (!selectedCourse || !selectedCourse.marks) return [];
    const dist = {};
    selectedCourse.marks.forEach(m => {
      const g = m.grade.toString();
      dist[g] = (dist[g] || 0) + 1;
    });
    return Object.keys(dist).sort((a,b) => parseFloat(a) - parseFloat(b)).map(k => ({ grade: k, count: dist[k] }));
  };

  const getPassFailData = () => {
    if (!selectedCourse || !selectedCourse.marks) return [];
    let pass = 0, fail = 0;
    selectedCourse.marks.forEach(m => {
      if (m.passed) pass++; else fail++;
    });
    return [
      { name: 'Passed', value: pass, fill: '#2E7D32' },
      { name: 'Failed', value: fail, fill: '#D32F2F' }
    ];
  };

  const getLongitudinalData = () => {
    if (!analyticsStudentTranscript.length) return [];
    const semMap = {};
    analyticsStudentTranscript.forEach(t => {
      if (!semMap[t.semester]) semMap[t.semester] = { sum: 0, count: 0 };
      semMap[t.semester].sum += t.grade;
      semMap[t.semester].count += 1;
    });
    return Object.keys(semMap).sort().map(sem => ({
      semester: sem,
      average: parseFloat((semMap[sem].sum / semMap[sem].count).toFixed(2))
    }));
  };

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: '100%' }}>
        <Box sx={{ mb: 3 }}>
          <Button startIcon={<ChevronLeftIcon />} onClick={() => { setSelectedCourse(null); setAnalyticsStudent(null); }} sx={{ color: '#424242', mb: 1 }}>Return to List</Button>
          <Typography variant="h3" sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>{selectedCourse.course_name}</Typography>
          <Box sx={{ display: 'flex', gap: 3, mt: 1, flexWrap: 'wrap' }}>
            <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400' }}>Average Grade: <strong>{selectedCourse.avg_grade}</strong></Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400' }}>Pass Rate: <strong style={{color: selectedCourse.pass_rate > 50 ? '#2E7D32' : '#D32F2F'}}>{selectedCourse.pass_rate}%</strong></Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: '400' }}>Total Submissions: <strong>{selectedCourse.total_attempts}</strong></Typography>
            <Button variant="contained" color="success" startIcon={<CloudUploadIcon />} onClick={() => {
                setUploadCourseInfo({...uploadCourseInfo, courseName: selectedCourse.course_name});
                setActiveTab('Batch Data Upload');
            }} sx={{ ml: 'auto', borderRadius: '8px' }}>Upload Data</Button>
            {!selectedCourse.is_archived && (
               <Button variant="outlined" color="secondary" startIcon={<ArchiveIcon />} onClick={() => handleArchiveCourse(selectedCourse.course_id, true)} sx={{ borderRadius: '8px' }}>Archive Course</Button>
            )}
            {selectedCourse.is_archived && (
               <Button variant="outlined" color="primary" startIcon={<RestoreIcon />} onClick={() => handleArchiveCourse(selectedCourse.course_id, false)} sx={{ ml: 'auto', borderRadius: '8px' }}>Restore Course</Button>
            )}
          </Box>
        </Box>
        
        
        {/* === ANALYTICS DASHBOARD SECTION === */}
        <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
          
          <Paper sx={{ p: 3, flex: 2, minWidth: 400, borderRadius: '24px' }}>
            <Typography variant="h6" fontWeight="700" mb={2}>Course Grade Distribution</Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={getGradeDistributionData()}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="grade" />
                <YAxis allowDecimals={false} />
                <RechartsTooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {getGradeDistributionData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={analyticsStudent && entry.grade === analyticsStudent.grade.toString() ? '#FF8F00' : '#1976d2'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {analyticsStudent && (
              <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={1}>
                Highlighting <strong>{analyticsStudent.student_name}'s</strong> grade ({analyticsStudent.grade})
              </Typography>
            )}
          </Paper>
          
          <Paper sx={{ p: 3, flex: 1, minWidth: 250, borderRadius: '24px' }}>
            <Typography variant="h6" fontWeight="700" mb={2}>Pass vs. Fail</Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={getPassFailData()} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5}>
                  {getPassFailData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>

          {analyticsStudent && (
            <Paper sx={{ p: 3, flex: 3, minWidth: 400, borderRadius: '24px' }}>
              <Typography variant="h6" fontWeight="700" mb={2}>{analyticsStudent.student_name}'s Longitudinal Trend</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={getLongitudinalData()}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="semester" />
                  <YAxis domain={[1, 5]} reversed={true} label={{ value: 'Average Grade', angle: -90, position: 'insideLeft' }} />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="average" stroke="#FF8F00" strokeWidth={3} dot={{ r: 5 }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          )}
        </Box>

        <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: '24px', overflow: 'hidden' }}>
          <Box sx={{ p: 3, borderBottom: '1px solid rgba(0, 0, 0, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" fontWeight="700">Detailed Course Marks</Typography>
              <Typography variant="body1" color="text.secondary">Marks per student per semester.</Typography>
            </Box>
            <TextField 
              label="Quick Search (Semester, Person...)" 
              size="small" 
              onChange={(e) => courseGridRef.current.api.setQuickFilter(e.target.value)} 
              sx={{ width: 300 }} 
            />
          </Box>
          <div className="ag-theme-alpine" style={{ width: '100%', padding: '16px' }}>
            <AgGridReact 
              ref={courseGridRef}
              domLayout="autoHeight"
              rowData={selectedCourse.marks} 
              columnDefs={[
                { field: 'student_id', headerName: 'Student ID', flex: 1 },
                { field: 'student_name', headerName: 'Name', flex: 2 },
                { field: 'program', headerName: 'Study Program', flex: 2 },
                { field: 'semester', headerName: 'Semester', flex: 1 },
                { field: 'grade', headerName: 'Grade', flex: 1, type: 'numericColumn', cellStyle: { fontWeight: 'bold' } },
                { field: 'passed', headerName: 'Passed?', flex: 1, cellRenderer: params => params.value ? 'Yes' : 'No' }
              ]} 
              defaultColDef={{ resizable: true, sortable: true, filter: true }} 
              animateRows={true} 
              pagination={true}
              paginationPageSize={20}
              onRowClicked={(e) => fetchAnalyticsStudentTranscript(e.data)}
              rowSelection="single"
            />
          </div>
        </Paper>
      </Box>
    </Fade>
  );

};
