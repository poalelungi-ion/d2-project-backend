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

export const BatchUploadWizard = (props) => {
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
  
    const steps = ['Upload file', 'Course', 'Map columns', 'Review & fix', 'Done'];

    const renderStepContent = () => {
      switch (activeStep) {
        case 0:
          return (
            <Box>
              <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary', fontSize: '1rem', maxWidth: 800 }}>
                Upload a spreadsheet from any lecturer. The system standardises the columns, flags problems automatically, and only saves once everything is clean.
              </Typography>
              <Box 
                sx={{ 
                  border: '2px dashed rgba(0,0,0,0.15)', 
                  borderRadius: '16px', 
                  p: 8, 
                  textAlign: 'center', 
                  mb: 6,
                  transition: 'all 0.3s ease', 
                  backgroundColor: uploadForm.file ? 'rgba(46, 125, 50, 0.05)' : 'transparent',
                  borderColor: uploadForm.file ? 'success.main' : 'rgba(0,0,0,0.15)',
                  '&:hover': { borderColor: 'primary.main', backgroundColor: 'rgba(183, 28, 28, 0.02)' } 
                }}
              >
                <input accept=".xlsx, .xls, .csv, .tsv, .ods" style={{ display: 'none' }} id="excel-upload-file" type="file" onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })} />
                <label htmlFor="excel-upload-file" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <Box sx={{ bgcolor: 'rgba(0,0,0,0.05)', borderRadius: '12px', p: 2, mb: 2, display: 'inline-flex' }}>
                    <DownloadIcon sx={{ color: '#757575', fontSize: 32 }} />
                  </Box>
                  <Typography variant="h6" fontWeight="700">Drag & drop .xlsx, .xls or .csv</Typography>
                  <Typography variant="body2" color="text.secondary">Every lecturer's file looks different — that's fine.</Typography>
                </label>
                {uploadForm.file && <Typography variant="body1" color="success.main" fontWeight="600" sx={{ mt: 2 }}>Selected: {uploadForm.file.name}</Typography>}
              </Box>

              <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, mb: 2, display: 'block' }}>
                DEMO FILES - PICK ONE TO SIMULATE AN UPLOAD
              </Typography>

              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                  <Card 
                    variant="outlined" 
                    onClick={() => setSelectedDemoFile('Klausur_DBS_WS2425.xlsx')}
                    sx={{ 
                      p: 2, height: '100%', cursor: 'pointer',
                      borderColor: selectedDemoFile === 'Klausur_DBS_WS2425.xlsx' ? 'primary.main' : 'rgba(0,0,0,0.12)',
                      borderWidth: selectedDemoFile === 'Klausur_DBS_WS2425.xlsx' ? 2 : 1,
                      bgcolor: selectedDemoFile === 'Klausur_DBS_WS2425.xlsx' ? 'rgba(183, 28, 28, 0.02)' : '#FFFFFF',
                      position: 'relative'
                    }}
                  >
                    {selectedDemoFile === 'Klausur_DBS_WS2425.xlsx' && <CheckCircleIcon color="primary" sx={{ position: 'absolute', top: 16, right: 16 }} />}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TableChartIcon sx={{ color: '#757575', mr: 1 }} />
                      <Typography variant="subtitle1" fontWeight="700">Klausur_DBS_WS2425.xlsx</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Single "Name" column (Last, First). Fachsemester given as a plain integer.
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#9E9E9E', display: 'block', mb: 2, fontFamily: 'monospace' }}>
                      Matrikelnr - Name - Studiengang - Fachsemester - Note
                    </Typography>
                    <Box sx={{ bgcolor: '#FFF3E0', color: '#E65100', px: 1.5, py: 0.5, borderRadius: 1, display: 'inline-block', fontSize: '0.75rem', fontWeight: 'bold' }}>
                      name not split &middot; format issues
                    </Box>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card 
                    variant="outlined" 
                    onClick={() => setSelectedDemoFile('results_export.csv')}
                    sx={{ 
                      p: 2, height: '100%', cursor: 'pointer',
                      borderColor: selectedDemoFile === 'results_export.csv' ? 'primary.main' : 'rgba(0,0,0,0.12)',
                      borderWidth: selectedDemoFile === 'results_export.csv' ? 2 : 1,
                      bgcolor: selectedDemoFile === 'results_export.csv' ? 'rgba(183, 28, 28, 0.02)' : '#FFFFFF',
                      position: 'relative'
                    }}
                  >
                    {selectedDemoFile === 'results_export.csv' && <CheckCircleIcon color="primary" sx={{ position: 'absolute', top: 16, right: 16 }} />}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TableChartIcon sx={{ color: '#757575', mr: 1 }} />
                      <Typography variant="subtitle1" fontWeight="700">results_export.csv</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Names already split, a percentage slipped into one grade.
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#9E9E9E', display: 'block', mb: 2, fontFamily: 'monospace' }}>
                      MatrNr - Vorname - Nachname - Program - Fachsemester - Grade
                    </Typography>
                    <Box sx={{ bgcolor: '#FFF3E0', color: '#E65100', px: 1.5, py: 0.5, borderRadius: 1, display: 'inline-block', fontSize: '0.75rem', fontWeight: 'bold' }}>
                      invalid grade value
                    </Box>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card 
                    variant="outlined" 
                    onClick={() => setSelectedDemoFile('ExamPoints-example.xlsx')}
                    sx={{ 
                      p: 2, height: '100%', cursor: 'pointer',
                      borderColor: selectedDemoFile === 'ExamPoints-example.xlsx' ? 'primary.main' : 'rgba(0,0,0,0.12)',
                      borderWidth: selectedDemoFile === 'ExamPoints-example.xlsx' ? 2 : 1,
                      bgcolor: selectedDemoFile === 'ExamPoints-example.xlsx' ? 'rgba(183, 28, 28, 0.02)' : '#FFFFFF',
                      position: 'relative'
                    }}
                  >
                    {selectedDemoFile === 'ExamPoints-example.xlsx' && <CheckCircleIcon color="primary" sx={{ position: 'absolute', top: 16, right: 16 }} />}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TableChartIcon sx={{ color: '#757575', mr: 1 }} />
                      <Typography variant="subtitle1" fontWeight="700">ExamPoints-example.xlsx</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Real exam-points export &mdash; per-question point columns and no Fachsemester column, so that required field stays empty.
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#9E9E9E', display: 'block', mb: 2, fontFamily: 'monospace', lineHeight: 1.2 }}>
                      Matrikelnr. - Last Name - First Name - Study Program - 1a - 1b - 2a - 2b - 3a - 3b - 4a - 4b - Points - Grade - Attended - Publish - Attest - Notes
                    </Typography>
                    <Box sx={{ bgcolor: '#FFF3E0', color: '#E65100', px: 1.5, py: 0.5, borderRadius: 1, display: 'inline-block', fontSize: '0.75rem', fontWeight: 'bold' }}>
                      missing required columns &middot; extra point columns
                    </Box>
                  </Card>
                </Grid>
              </Grid>

              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 'auto', pt: 2 }}>
                <Button variant="contained" color="primary" size="large" onClick={() => setActiveStep(1)} sx={{ borderRadius: '8px', px: 4, fontWeight: 'bold' }}>
                  Continue &rarr;
                </Button>
              </Box>
            </Box>
          );
        
        case 1:
          return (
            <Box>
              <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary', fontSize: '1rem', maxWidth: 800 }}>
                A table is always for one course and one semester &mdash; that can't vary within a file. Tell us which one <Box component="span" sx={{ bgcolor: '#EEEEEE', px: 1, borderRadius: 1, fontFamily: 'monospace' }}>{selectedDemoFile}</Box> is for.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, maxWidth: 600 }}>
                <Box>
                  <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, display: 'block', mb: 1 }}>COURSE NUMBER</Typography>
                  <TextField fullWidth variant="outlined" value={uploadCourseInfo.courseNumber} onChange={(e) => setUploadCourseInfo({...uploadCourseInfo, courseNumber: e.target.value})} />
                </Box>
                <Box>
                  <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, display: 'block', mb: 1 }}>COURSE NAME</Typography>
                  <TextField fullWidth variant="outlined" value={uploadCourseInfo.courseName} onChange={(e) => setUploadCourseInfo({...uploadCourseInfo, courseName: e.target.value})} />
                </Box>
                <Box>
                  <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, display: 'block', mb: 1 }}>ECTS (CREDITS FOR THIS COURSE)</Typography>
                  <TextField fullWidth variant="outlined" value={uploadCourseInfo.ects} onChange={(e) => setUploadCourseInfo({...uploadCourseInfo, ects: e.target.value})} />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>Same course number but different credits (e.g. 6 vs 8) counts as a separate course instance.</Typography>
                </Box>
                <Box>
                  <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, display: 'block', mb: 1 }}>EXAM DATE</Typography>
                  <Box sx={{ display: 'inline-flex', bgcolor: '#F5F5F5', borderRadius: '8px', p: 0.5 }}>
                    <Button 
                      variant={uploadCourseInfo.examDate === '1st date' ? 'contained' : 'text'} 
                      color={uploadCourseInfo.examDate === '1st date' ? 'inherit' : 'inherit'}
                      onClick={() => setUploadCourseInfo({...uploadCourseInfo, examDate: '1st date'})}
                      sx={{ borderRadius: '6px', px: 2, bgcolor: uploadCourseInfo.examDate === '1st date' ? '#212121' : 'transparent', color: uploadCourseInfo.examDate === '1st date' ? '#FFF' : '#757575', fontWeight: 'bold', '&:hover': { bgcolor: uploadCourseInfo.examDate === '1st date' ? '#212121' : '#E0E0E0' } }}
                    >
                      1st date
                    </Button>
                    <Button 
                      variant={uploadCourseInfo.examDate === '2nd date' ? 'contained' : 'text'} 
                      color={uploadCourseInfo.examDate === '2nd date' ? 'inherit' : 'inherit'}
                      onClick={() => setUploadCourseInfo({...uploadCourseInfo, examDate: '2nd date'})}
                      sx={{ borderRadius: '6px', px: 2, bgcolor: uploadCourseInfo.examDate === '2nd date' ? '#212121' : 'transparent', color: uploadCourseInfo.examDate === '2nd date' ? '#FFF' : '#757575', fontWeight: 'bold', '&:hover': { bgcolor: uploadCourseInfo.examDate === '2nd date' ? '#212121' : '#E0E0E0' } }}
                    >
                      2nd date
                    </Button>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>Lets you compare how the first and second exam date went for this course later.</Typography>
                </Box>
                <Box>
                  <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, display: 'block', mb: 1 }}>SEMESTER</Typography>
                  <TextField fullWidth variant="outlined" value={uploadCourseInfo.semester} onChange={(e) => setUploadCourseInfo({...uploadCourseInfo, semester: e.target.value})} />
                </Box>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 6 }}>
                <Button variant="outlined" color="inherit" onClick={() => setActiveStep(0)} sx={{ borderRadius: '8px', px: 3, fontWeight: 'bold' }}>
                  &larr; Back
                </Button>
                <Button variant="contained" color="primary" size="large" onClick={() => setActiveStep(2)} sx={{ borderRadius: '8px', px: 4, fontWeight: 'bold' }}>
                  Continue &rarr;
                </Button>
              </Box>
            </Box>
          );

        case 2:
          return (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                <Box sx={{ bgcolor: 'rgba(0,0,0,0.05)', color: '#212121', px: 1.5, py: 0.5, borderRadius: 1, fontFamily: 'monospace', fontWeight: 'bold', mr: 2 }}>{selectedDemoFile}</Box>
                <Typography variant="body2" color="text.secondary">5 columns &middot; 8 rows detected</Typography>
              </Box>

              <Grid container spacing={4}>
                <Grid item xs={12} md={8}>
                  {/* Column Mapping Table */}
                  <Box sx={{ border: '1px solid rgba(0,0,0,0.1)', borderRadius: '12px', overflow: 'hidden', mb: 3 }}>
                    <Box sx={{ display: 'flex', bgcolor: '#F5F5F5', px: 3, py: 1.5, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
                      <Typography variant="overline" sx={{ width: '40%', fontWeight: '700', color: '#757575' }}>COLUMN IN FILE</Typography>
                      <Typography variant="overline" sx={{ width: '40%', fontWeight: '700', color: '#757575' }}>MAPS TO</Typography>
                      <Typography variant="overline" sx={{ width: '20%', fontWeight: '700', color: '#757575', textAlign: 'right' }}>STATUS</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2, borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
                      <Box sx={{ width: '40%' }}>
                        <Typography variant="subtitle2" fontWeight="700">Matrikelnr</Typography>
                        <Typography variant="caption" color="text.secondary">e.g. 1012345</Typography>
                      </Box>
                      <Box sx={{ width: '40%' }}>
                        <TextField size="small" fullWidth value="Matrikelnummer" InputProps={{ readOnly: true }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: '#FFF' } }} />
                      </Box>
                      <Box sx={{ width: '20%', textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: '#2E7D32', fontWeight: '700' }}>Mapped</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2, borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
                      <Box sx={{ width: '40%' }}>
                        <Typography variant="subtitle2" fontWeight="700">Name</Typography>
                        <Typography variant="caption" color="text.secondary">e.g. Schneider, Lena</Typography>
                      </Box>
                      <Box sx={{ width: '40%' }}>
                        <TextField size="small" fullWidth value="Full name (auto-split)" InputProps={{ readOnly: true }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: '#FFF' } }} />
                      </Box>
                      <Box sx={{ width: '20%', textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: '#1976D2', fontWeight: '700' }}>Name &rarr; split</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2, borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
                      <Box sx={{ width: '40%' }}>
                        <Typography variant="subtitle2" fontWeight="700">Studiengang</Typography>
                        <Typography variant="caption" color="text.secondary">e.g. B.Sc. AINF</Typography>
                      </Box>
                      <Box sx={{ width: '40%' }}>
                        <TextField size="small" fullWidth value="Study program" InputProps={{ readOnly: true }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: '#FFF' } }} />
                      </Box>
                      <Box sx={{ width: '20%', textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: '#2E7D32', fontWeight: '700' }}>Mapped</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2, borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
                      <Box sx={{ width: '40%' }}>
                        <Typography variant="subtitle2" fontWeight="700">Fachsemester</Typography>
                        <Typography variant="caption" color="text.secondary">e.g. 3</Typography>
                      </Box>
                      <Box sx={{ width: '40%' }}>
                        <TextField size="small" fullWidth value="Semester (Fachsemester count)" InputProps={{ readOnly: true }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: '#FFF' } }} />
                      </Box>
                      <Box sx={{ width: '20%', textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: '#2E7D32', fontWeight: '700' }}>Mapped</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2 }}>
                      <Box sx={{ width: '40%' }}>
                        <Typography variant="subtitle2" fontWeight="700">Note</Typography>
                        <Typography variant="caption" color="text.secondary">e.g. 1.7</Typography>
                      </Box>
                      <Box sx={{ width: '40%' }}>
                        <TextField size="small" fullWidth value="Grade" InputProps={{ readOnly: true }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: '#FFF' } }} />
                      </Box>
                      <Box sx={{ width: '20%', textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: '#2E7D32', fontWeight: '700' }}>Mapped</Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* Name Split Helper */}
                  <Box sx={{ bgcolor: 'rgba(103, 58, 183, 0.05)', borderRadius: '12px', p: 3, display: 'flex', alignItems: 'center', gap: 2, border: '1px solid rgba(103, 58, 183, 0.2)' }}>
                    <Typography variant="body2" sx={{ color: '#512DA8', fontWeight: '600' }}>A single name column was found. Split it as:</Typography>
                    <Box sx={{ display: 'inline-flex', bgcolor: '#FFF', borderRadius: '8px', p: 0.5, border: '1px solid rgba(0,0,0,0.1)' }}>
                      <Button 
                        variant={nameSplitRule === 'Last, First' ? 'contained' : 'text'} 
                        color={nameSplitRule === 'Last, First' ? 'inherit' : 'inherit'}
                        onClick={() => setNameSplitRule('Last, First')}
                        sx={{ borderRadius: '6px', px: 1, minWidth: 0, bgcolor: nameSplitRule === 'Last, First' ? '#212121' : 'transparent', color: nameSplitRule === 'Last, First' ? '#FFF' : '#757575', fontWeight: 'bold', fontSize: '0.8rem', '&:hover': { bgcolor: nameSplitRule === 'Last, First' ? '#212121' : '#F5F5F5' } }}
                      >
                        Last, First
                      </Button>
                      <Button 
                        variant={nameSplitRule === 'First Last' ? 'contained' : 'text'} 
                        color={nameSplitRule === 'First Last' ? 'inherit' : 'inherit'}
                        onClick={() => setNameSplitRule('First Last')}
                        sx={{ borderRadius: '6px', px: 1, minWidth: 0, bgcolor: nameSplitRule === 'First Last' ? '#212121' : 'transparent', color: nameSplitRule === 'First Last' ? '#FFF' : '#757575', fontWeight: 'bold', fontSize: '0.8rem', '&:hover': { bgcolor: nameSplitRule === 'First Last' ? '#212121' : '#F5F5F5' } }}
                      >
                        First Last
                      </Button>
                    </Box>
                    <Typography variant="caption" sx={{ color: '#757575' }}>&mdash; Schneider, Lena</Typography>
                  </Box>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ borderRadius: '12px', p: 3, bgcolor: '#FAFAFA' }}>
                    <Typography variant="overline" sx={{ fontWeight: '800', color: '#424242', mb: 2, display: 'block' }}>TARGET SCHEMA</Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mb: 3 }}>
                      {[
                        { name: 'Matrikelnummer', req: 'required' },
                        { name: 'First name', req: 'optional' },
                        { name: 'Last name', req: 'required' },
                        { name: 'Study program', req: 'required' },
                        { name: 'Semester (Fachsemester)', req: 'optional' },
                        { name: 'Grade', req: 'required' }
                      ].map((f) => (
                        <Box key={f.name} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <CheckCircleIcon sx={{ fontSize: 16, color: '#2E7D32', mr: 1 }} />
                            <Typography variant="body2" sx={{ fontWeight: '600' }}>{f.name}</Typography>
                          </Box>
                          <Typography variant="caption" sx={{ color: '#9E9E9E' }}>{f.req}</Typography>
                        </Box>
                      ))}
                    </Box>
                    <Typography variant="caption" sx={{ color: '#757575', display: 'block', lineHeight: 1.4 }}>
                      Grades are validated as German marks (1.0 &ndash; 5.0). Course, course number, ECTS and the course semester were already set in the previous step and apply to every row. "Semester" below is the student's Fachsemester count.
                    </Typography>
                  </Card>
                </Grid>
              </Grid>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 6 }}>
                <Button variant="outlined" color="inherit" onClick={() => setActiveStep(1)} sx={{ borderRadius: '8px', px: 3, fontWeight: 'bold' }}>
                  &larr; Back
                </Button>
                <Button variant="contained" color="primary" size="large" onClick={handleUpload} sx={{ borderRadius: '8px', px: 4, fontWeight: 'bold' }}>
                  Standardise &amp; review &rarr;
                </Button>
              </Box>
            </Box>
          );
        
        case 3:
          const hasErrors = previewData.some(r => !r.is_valid);
          return (
            <Box sx={{ py: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h5" fontWeight="700">Review Data &amp; Validation</Typography>
                <Typography variant="body1" color="text.secondary">
                  Please review the parsed records. Rows missing required fields are highlighted.
                </Typography>
              </Box>
              
              {hasErrors && (
                <Box sx={{ bgcolor: 'rgba(211, 47, 47, 0.1)', borderLeft: '4px solid #d32f2f', p: 2, mb: 3, borderRadius: '4px' }}>
                  <Typography variant="body1" color="error" fontWeight="bold">
                    Warning: Some records are missing required fields. You can still import, but incomplete rows will be marked as "Unknown".
                  </Typography>
                </Box>
              )}

              <div className="ag-theme-alpine" style={{ height: '400px', width: '100%', marginBottom: '24px' }}>
                <AgGridReact 
                  rowData={previewData}
                  onGridReady={(params) => setGridApi(params.api)}
                  onRowDataUpdated={(params) => {
                    params.api.forEachNode((node) => {
                      const g = String(node.data.grade).toLowerCase().trim();
                      if (!['na', 'ta', 'ne', 'nan', '', 'at'].includes(g) && node.data.is_valid) {
                        node.setSelected(true);
                      }
                    });
                  }}
                  onRowSelected={(event) => {
                    if (event.node.isSelected()) {
                      const g = String(event.data.grade).toLowerCase().trim();
                      if (['na', 'ta', 'ne', 'nan', '', 'at'].includes(g)) {
                        event.node.setDataValue('grade', '5.0');
                      }
                    }
                  }}
                  rowSelection="multiple"
                  columnDefs={[
                    { field: 'student_id', headerName: 'Matrikelnr', checkboxSelection: true, headerCheckboxSelection: true, editable: true },
                    { field: 'first_name', headerName: 'First Name', editable: true },
                    { field: 'last_name', headerName: 'Last Name', editable: true },
                    { field: 'program', headerName: 'Program', editable: true },
                    { field: 'semester', headerName: 'Semester', editable: true },
                    { field: 'grade', headerName: 'Grade', editable: true },
                    { 
                      field: 'missing_fields', 
                      headerName: 'Validation Issues', 
                      flex: 1,
                      cellRenderer: params => {
                        if (!params.value || params.value.length === 0) return <span style={{color: '#2e7d32', fontWeight: 'bold'}}>Valid</span>;
                        return <span style={{color: '#d32f2f', fontWeight: 'bold'}}>Missing: {params.value.join(', ')}</span>;
                      }
                    }
                  ]}
                  defaultColDef={{ resizable: true, sortable: true }}
                  getRowStyle={params => {
                    if (!params.data.is_valid) {
                      return { background: 'rgba(211, 47, 47, 0.05)' };
                    }
                  }}
                />
              </div>

              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Button variant="outlined" color="inherit" onClick={() => setActiveStep(2)} sx={{ borderRadius: '8px', px: 3, fontWeight: 'bold' }}>&larr; Back</Button>
                <Button variant="contained" color="primary" size="large" onClick={handleConfirmUpload} sx={{ borderRadius: '8px', px: 4, fontWeight: 'bold' }}>Complete Import</Button>
              </Box>
            </Box>
          );
          
        case 4:
          return (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <CheckCircleIcon color="success" sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h5" fontWeight="700" sx={{ mb: 1 }}>Import Successful</Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>The grades have been safely stored in the database.</Typography>
              <Button variant="outlined" color="primary" onClick={() => setActiveStep(0)} sx={{ borderRadius: '8px', px: 3, fontWeight: 'bold' }}>Import another file</Button>
            </Box>
          );
          
        default:
          return null;
      }
    };

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 4, maxWidth: 1100, margin: '0 auto', width: '100%' }}>
          <Typography variant="h4" fontWeight="800" gutterBottom sx={{ color: '#212121', mb: 1 }}>
            Import grades
          </Typography>
          
          <Box sx={{ width: '100%', mb: 6 }}>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ '& .MuiStepLabel-label': { fontWeight: '600' }, '& .MuiStepIcon-root.Mui-active': { color: '#B71C1C' }, '& .MuiStepIcon-root.Mui-completed': { color: '#B71C1C' } }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>

          {renderStepContent()}
        </Box>
      </Fade>
    );
  };
  // === ANALYTICS HELPERS ===
  /**
   * [User Story 6: Visual Analytics Dashboard]
   * Fetches the complete grade history for a selected student to plot their longitudinal trend.
   * @param {Object} student - The student object selected from the course roster grid.
   */
  const fetchAnalyticsStudentTranscript = async (student) => {
    setAnalyticsStudent(student);
    try {
      const res = await fetch(`http://localhost:8000/api/students/${student.student_id}`, {
        headers: { 'Authorization': 'Bearer sse-staff-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setAnalyticsStudentTranscript(data.transcript || []);
      }
    } catch (e) {
      console.error("Failed to fetch student transcript for analytics", e);
    }
  };

  /**
   * [User Story 6: Visual Analytics Dashboard]
   * Computes the histogram distribution of grades for the currently selected course.
   * @returns {Array} An array of objects formatted for Recharts BarChart ({grade, count}).
   */
  const getGradeDistributionData = () => {
    if (!selectedCourse || !selectedCourse.marks) return [];
    const dist = {};
    selectedCourse.marks.forEach(m => {
      const g = m.grade.toString();
      dist[g] = (dist[g] || 0) + 1;
    });
    return Object.keys(dist).sort((a,b) => parseFloat(a) - parseFloat(b)).map(k => ({ grade: k, count: dist[k] }));
  };

  /**
   * [User Story 6: Visual Analytics Dashboard]
   * Calculates the overall pass vs. fail ratio for the currently selected course.
   * @returns {Array} An array of objects formatted for Recharts PieChart.
   */
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

  /**
   * [User Story 6: Visual Analytics Dashboard]
   * Aggregates the student's historical transcript into a chronological semester-over-semester average.
   * @returns {Array} An array of objects formatted for Recharts LineChart ({semester, average}).
   */
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

