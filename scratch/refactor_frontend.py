import os
import re

app_file = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\App.jsx'
with open(app_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

blocks = [
    ('renderDashboard', 'AnalysisHub', 'features', 614, 678),
    ('renderUploadForm', 'BatchUploadWizard', 'features', 680, 1199),
    ('renderCourseDetail', 'CourseDetail', 'features', 1201, 1318),
    ('renderCourses', 'CoursesAdmin', 'features', 1320, 1447),
    ('renderStudentDetail', 'StudentDetail', 'features', 1449, 1514),
    ('renderStudents', 'StudentsAdmin', 'features', 1516, 1608),
    ('renderSystemLogs', 'SystemLogs', 'features', 1610, 1651)
]

extracted_files = {}

for func_name, comp_name, folder, start, end in blocks:
    block_lines = lines[start-1 : end]
    block_str = "".join(block_lines)
    
    comp_code = f"""import React, {{ useState, useEffect }} from 'react';
import {{ 
  Box, Typography, Grid, Card, CardContent, Button, TextField, 
  Stepper, Step, StepLabel, Select, MenuItem, FormControl, InputLabel,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  LinearProgress, Fade, Collapse, Alert, Avatar, Tooltip, Tab, Tabs
}} from '@mui/material';
import {{
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
}} from 'recharts';
import {{
  UploadFile as UploadFileIcon, CheckCircle as CheckCircleIcon,
  Warning as WarningIcon, Error as ErrorIcon, Delete as DeleteIcon,
  Edit as EditIcon, Add as AddIcon, Refresh as RefreshIcon,
  MoreVert as MoreVertIcon, School as SchoolIcon, Assessment as AssessmentIcon,
  Timeline as TimelineIcon, Save as SaveIcon, Close as CloseIcon,
  ArrowBack as ArrowBackIcon, Check as CheckIcon,
  Dashboard as DashboardIcon, TableChart as TableChartIcon, Person as PersonIcon,
  History as HistoryIcon, ExpandMore as ExpandMoreIcon, WarningAmber as WarningAmberIcon
}} from '@mui/icons-material';
import {{ TABS, STEPS }} from '../../utils/constants';

export const {comp_name} = (props) => {{
  const {{ 
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
  }} = props;
"""
    if block_str.strip().endswith(');'):
        body_inner = block_str[block_str.find('(')+1:block_str.rfind(')')]
        body_inner = re.sub(rf'const {func_name}\s*=\s*\(\)\s*=>\s*\(', 'return (', block_str)
        comp_code += body_inner
    else:
        body_inner = re.sub(rf'const {func_name}\s*=\s*\(\)\s*=>\s*{{', '', block_str)
        if body_inner.rstrip().endswith('}'):
            body_inner = body_inner.rstrip()[:-1]
        comp_code += body_inner
        
    comp_code += "\n};\n"
    extracted_files[comp_name] = (folder, comp_code)

for func_name, comp_name, folder, start, end in reversed(blocks):
    del lines[start-1 : end]
    lines.insert(start-1, f"  // Extracted {comp_name}\n")

new_content = "".join(lines)

app_state_code = """
  const appState = {
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
  };

"""
return_idx = new_content.rfind('  return (')
new_content = new_content[:return_idx] + app_state_code + new_content[return_idx:]

new_content = new_content.replace('{renderDashboard()}', '<AnalysisHub {...appState} />')
new_content = new_content.replace('{renderUploadForm()}', '<BatchUploadWizard {...appState} />')
new_content = new_content.replace('{renderCourseDetail()}', '<CourseDetail {...appState} />')
new_content = new_content.replace('{renderCourses()}', '<CoursesAdmin {...appState} />')
new_content = new_content.replace('{renderStudentDetail()}', '<StudentDetail {...appState} />')
new_content = new_content.replace('{renderStudents()}', '<StudentsAdmin {...appState} />')
new_content = new_content.replace('{renderSystemLogs()}', '<SystemLogs {...appState} />')

imports = "\n".join([f"import {{ {name} }} from './components/{folder}/{name}';" for name, (folder, code) in extracted_files.items()])
new_content = new_content.replace("import { getGlassTheme } from './theme';", "import { getGlassTheme } from './theme';\n" + imports)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

for name, (folder, code) in extracted_files.items():
    path = rf'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\components\{folder}\{name}.jsx'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
