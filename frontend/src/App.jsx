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

const getGlassTheme = (mode) => createTheme({
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

export default function App() {
  // === STATE DEFINITIONS & HOOKS ===
  const [themeMode, setThemeMode] = useState('light');
  const glassTheme = React.useMemo(() => getGlassTheme(themeMode), [themeMode]);

  useEffect(() => {
    document.body.setAttribute('data-theme', themeMode);
  }, [themeMode]);

  const toggleTheme = () => {
    setThemeMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const gridRef = useRef();
  const studentGridRef = useRef();
  const courseGridRef = useRef();
  const [activeTab, setActiveTab] = useState('Analysis Hub');
  const [coursesData, setCoursesData] = useState([]);
  const [studentsData, setStudentsData] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [analyticsStudent, setAnalyticsStudent] = useState(null);
  const [analyticsStudentTranscript, setAnalyticsStudentTranscript] = useState([]);
  
  const [courseFormOpen, setCourseFormOpen] = useState(false);
  const [courseFormMode, setCourseFormMode] = useState('create');
  const [courseForm, setCourseForm] = useState({ course_id: '', course_name: '', semester: '', study_program: '', professor: '' });
  const [courseFormErrors, setCourseFormErrors] = useState({});
  const [editCourseVersion, setEditCourseVersion] = useState(1);

  const [addGradeDialogOpen, setAddGradeDialogOpen] = useState(false);
  const [addGradeForm, setAddGradeForm] = useState({ course_id: '', semester: 'WiSe23/24', grade: 1.0 });
  const [archiveTab, setArchiveTab] = useState(0);
  
  const [newCourseName, setNewCourseName] = useState("");
  const [uploadForm, setUploadForm] = useState({ semester: '', course: '', file: null });
  const [previewData, setPreviewData] = useState([]);
  const [gridApi, setGridApi] = useState(null);
  const [uploadPreview, setUploadPreview] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedDemoFile, setSelectedDemoFile] = useState('Klausur_DBS_WS2425.xlsx');
  
  // Batch Data Upload UI State
  const [uploadCourseInfo, setUploadCourseInfo] = useState({
    courseNumber: '3545',
    courseName: 'SE Tools Lab',
    ects: '6',
    examDate: '1st date',
    semester: 'WiSe 2024/25'
  });
  const [nameSplitRule, setNameSplitRule] = useState('Last, First');
  const [stats, setStats] = useState({ kpis: {}, toughest_courses: [], atRisk: [] });
  const [toast, setToast] = useState({ open: false, message: '', severity: 'success' });


  // Columns for student-specific grid
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [coursesSortBy, setCoursesSortBy] = useState('name');
  const [studentViewMode, setStudentViewMode] = useState('table');
  const [studentSearchQuery, setStudentSearchQuery] = useState('');
  const [studentFormOpen, setStudentFormOpen] = useState(false);
  const [studentFormMode, setStudentFormMode] = useState('create');
  const [studentForm, setStudentForm] = useState({ student_id: '', first_name: '', last_name: '', program: '', status: 'active' });
  const [studentFormErrors, setStudentFormErrors] = useState({});
  const [editStudentVersion, setEditStudentVersion] = useState(1);

  const [searchQuery, setSearchQuery] = useState('');
  const [coursesPage, setCoursesPage] = useState(1);
  const [viewMode, setViewMode] = useState('table');
  const [newCourseId, setNewCourseId] = useState("");
  const [studentColumnDefs] = useState([
    { field: 'result_id', headerName: 'ID', hide: true },
    { field: 'attempt', headerName: 'Attempt #', editable: false, flex: 0.8 },
    { field: 'semester', headerName: 'Semester', editable: false, flex: 1 },
    { field: 'course', headerName: 'Course', editable: false, flex: 2 },
    { field: 'grade', headerName: 'Grade (1.0-5.0)', editable: true, flex: 1, type: 'numericColumn', cellStyle: { fontWeight: 'bold', backgroundColor: 'rgba(0, 0, 0, 0.05)' } },
    { field: 'passed', headerName: 'Passed?', editable: true, flex: 1, cellEditor: 'agCheckboxCellEditor' }
  ]);

  // === API DATA FETCHING ===
  /**
   * Fetches global KPI stats, courses, and students data from the backend.
   * Populates the primary dashboard and grid tables.
   */
  const fetchData = async () => {
    try {
      const [statRes, courseRes, studentRes] = await Promise.all([
        fetch('http://localhost:8000/api/stats/'),
        fetch('http://localhost:8000/api/courses/'),
        fetch('http://localhost:8000/api/students/')
      ]);
      setStats(await statRes.json());
      setCoursesData(await courseRes.json());
      setStudentsData(await studentRes.json());
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoadingCourses(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const fetchStudentTranscript = async (student_id) => {
    try {
      const res = await fetch(`http://localhost:8000/api/students/${student_id}`);
      const data = await res.json();
      setSelectedStudent(data);
    } catch (e) {
      console.error('Failed to fetch transcript');
    }
  };

  const onExportClick = useCallback(() => {
    if (gridRef.current) gridRef.current.api.exportDataAsCsv();
  }, []);

  const saveGradesToDB = async (gridReference) => {
    const rowDataArray = [];
    gridReference.current.api.forEachNode(node => rowDataArray.push(node.data));
    try {
      const res = await fetch('http://localhost:8000/api/grades/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rowDataArray)
      });
      if (res.ok) {
        setToast({ open: true, message: 'Database updated successfully!', severity: 'success' });
        fetchData();
        if (selectedStudent) fetchStudentTranscript(selectedStudent.student_id); 
      } else {
        const error = await res.json();
        setToast({ open: true, message: res.status === 409 ? 'Update failed: Data was modified by another user. Please refresh.' : `Validation Error: ${error.detail}`, severity: 'error' });
        if (res.status === 409) fetchData(); // Auto refresh
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error occurred', severity: 'error' });
    }
  };

  
  const openCourseForm = (course = null) => {
    if (course) {
      setCourseFormMode('edit');
      setCourseForm({
        course_id: course.course_id || '',
        course_name: course.course_name || '',
        semester: course.semester || '',
        study_program: course.study_program || '',
        professor: course.assigned_professor || ''
      });
      setEditCourseVersion(course.version || 1);
    } else {
      setCourseFormMode('create');
      setCourseForm({ course_id: '', course_name: '', semester: '', study_program: '', professor: '' });
    }
    setCourseFormErrors({});
    setCourseFormOpen(true);
  };

  
  const courseColumnDefs = useMemo(() => [
    { field: 'course_id', headerName: 'ID', flex: 0.8 },
    { field: 'course_name', headerName: 'Name', flex: 2 },
    { field: 'semester', headerName: 'Semester', flex: 1 },
    { field: 'assigned_professor', headerName: 'Professor', flex: 1.5 },
    { field: 'total_attempts', headerName: 'Submissions', flex: 1 },
    { 
      field: 'pass_rate', 
      headerName: 'Pass Rate', 
      flex: 1, 
      cellRenderer: (params) => {
        const color = params.value > 50 ? '#2E7D32' : '#D32F2F';
        return <span style={{ color: color, fontWeight: 'bold' }}>{params.value}%</span>;
      }
    },
    { field: 'avg_grade', headerName: 'Avg Grade', flex: 1 },
    { 
      field: 'actions', 
      headerName: 'Actions', 
      flex: 0.8,
      sortable: false,
      filter: false,
      cellRenderer: (params) => (
        <IconButton size="small" onClick={(e) => { e.stopPropagation(); openCourseForm(params.data); }}>
          <EditIcon fontSize="small" />
        </IconButton>
      )
    }
  ], []);

  
  /**
   * Opens the unified Create/Edit Student Profile dialog.
   * For editing, it pre-populates fields and cleanly splits the full name into first/last name.
   */
  const openStudentForm = (student = null) => {
    if (student) {
      setStudentFormMode('edit');
      const nameParts = (student.name || '').split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';
      setStudentForm({
        student_id: student.student_id || '',
        first_name: first_name,
        last_name: last_name,
        program: student.program || '',
        status: student.status || 'active'
      });
      setEditStudentVersion(student.version || 1);
    } else {
      setStudentFormMode('create');
      setStudentForm({ student_id: '', first_name: '', last_name: '', program: '', status: 'active' });
    }
    setStudentFormErrors({});
    setStudentFormOpen(true);
  };

  const validateStudentForm = () => {
    const errors = {};
    if (!studentForm.first_name.trim()) errors.first_name = "First Name is mandatory";
    if (!studentForm.last_name.trim()) errors.last_name = "Last Name is mandatory";
    if (!studentForm.student_id.toString().trim()) errors.student_id = "Student ID is mandatory";
    if (!studentForm.program.trim()) errors.program = "Study Program is mandatory";
    setStudentFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * [User Story: Profile Creation] & [User Story: Profile Editing]
   * Validates mandatory frontend fields (First Name, Last Name, Student ID, Program).
   * Concatenates First & Last name into a single string for backend compatibility.
   * Triggers success toast notifications matching the explicit Acceptance Criteria.
   */
  const handleSaveStudent = async () => {
    if (!validateStudentForm()) return;
    
    const isEdit = studentFormMode === 'edit';
    const url = isEdit ? `http://localhost:8000/api/students/${studentForm.student_id}` : 'http://localhost:8000/api/students/';
    const method = isEdit ? 'PUT' : 'POST';
    
    const payload = {
      student_id: parseInt(studentForm.student_id),
      new_student_id: isEdit ? parseInt(studentForm.student_id) : undefined,
      name: `${studentForm.first_name.trim()} ${studentForm.last_name.trim()}`,
      program: studentForm.program,
      status: studentForm.status
    };
    if (isEdit) payload.version = editStudentVersion;

    try {
      const res = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer sse-staff-token'
        },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setToast({ open: true, message: isEdit ? 'Student profile updated' : 'Student profile created', severity: 'success' });
        setStudentFormOpen(false);
        fetchData();
      } else {
        const error = await res.json();
        setToast({ open: true, message: `Error: ${error.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };

  const studentRosterColumnDefs = useMemo(() => [
    { field: 'student_id', headerName: 'ID', flex: 1 },
    { field: 'name', headerName: 'Name', flex: 2 },
    { field: 'program', headerName: 'Study Program', flex: 2 },
    { field: 'total_exams', headerName: 'Exams Taken', flex: 1 },
    { field: 'avg_grade', headerName: 'Avg Grade', flex: 1 },
    { 
      field: 'status', 
      headerName: 'Status', 
      flex: 1,
      cellRenderer: (params) => {
        const color = params.value === 'active' ? '#1976D2' : (params.value === 'graduated' ? '#2E7D32' : '#D32F2F');
        return <span style={{ color, fontWeight: 'bold' }}>{params.value.toUpperCase()}</span>;
      }
    },
    { 
      field: 'actions', 
      headerName: 'Actions', 
      flex: 1,
      sortable: false,
      filter: false,
      cellRenderer: (params) => (
        <IconButton size="small" onClick={(e) => { e.stopPropagation(); openStudentForm(params.data); }}>
          <EditIcon fontSize="small" />
        </IconButton>
      )
    }
  ], []);

  const validateCourseForm = () => {
    const errors = {};
    if (!courseForm.course_name.trim()) errors.course_name = "Course Name is mandatory";
    if (!courseForm.course_id.toString().trim()) errors.course_id = "Course ID is mandatory";
    if (!courseForm.semester.trim()) errors.semester = "Semester is mandatory";
    if (!courseForm.study_program.trim()) errors.study_program = "Study Program is mandatory";
    setCourseFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveCourse = async () => {
    if (!validateCourseForm()) return;
    
    const isEdit = courseFormMode === 'edit';
    const url = isEdit ? `http://localhost:8000/api/courses/${courseForm.course_id}` : 'http://localhost:8000/api/courses/';
    const method = isEdit ? 'PUT' : 'POST';
    
    const payload = {
      course_id: courseForm.course_id,
      new_course_id: isEdit ? parseInt(courseForm.course_id) : undefined,
      course_name: courseForm.course_name,
      semester: courseForm.semester,
      study_program: courseForm.study_program,
      professor: courseForm.professor || "Not Assigned"
    };
    if (isEdit) payload.version = editCourseVersion;

    try {
      const res = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer sse-staff-token'
        },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setToast({ open: true, message: `Course successfully ${isEdit ? 'updated' : 'created'}`, severity: 'success' });
        setCourseFormOpen(false);
        fetchData();
      } else {
        const error = await res.json();
        setToast({ open: true, message: `Error: ${error.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };


  // === FILE UPLOAD & PREVIEW (STEP 2 -> 3) ===
  /**
   * [User Story: File Upload & Format Support]
   * Submits the chosen file (Excel/CSV/etc.) to the backend for preview generation.
   */
  const handleUploadSubmit = async () => {
    if (!uploadForm.file || !uploadForm.semester || !uploadForm.course) {
      setToast({ open: true, message: 'Please fill all fields and select a file.', severity: 'warning' });
      return;
    }
    const formData = new FormData();
    formData.append('file', uploadForm.file);
    formData.append('semester', uploadForm.semester);
    formData.append('course', uploadForm.course);

    try {
      const res = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setToast({ open: true, message: 'Excel file uploaded and processed successfully!', severity: 'success' });
        setUploadPreview(data.preview);
        setUploadForm({ semester: '', course: '', file: null });
        fetchData();
      } else {
        const error = await res.json();
        setToast({ open: true, message: `Upload Error: ${error.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error occurred during upload', severity: 'error' });
    }
  };

  const updateStudentProgram = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/students/${selectedStudent.student_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program: selectedStudent.program, version: selectedStudent.version })
      });
      if (res.ok) {
        setToast({ open: true, message: 'Student program updated successfully!', severity: 'success' });
        fetchData();
      } else {
        setToast({ open: true, message: 'Failed to update program', severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };

  const handleArchiveCourse = async (course_id, is_archived) => {
    try {
      const res = await fetch(`http://localhost:8000/api/courses/${course_id}/archive`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_archived })
      });
      if (res.ok) {
        setToast({ open: true, message: is_archived ? 'Course archived successfully!' : 'Course restored successfully!', severity: 'success' });
        setSelectedCourse(null);
        fetchData();
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };

  const handleStudentStatus = async (student_id, status) => {
    try {
      const res = await fetch(`http://localhost:8000/api/students/${student_id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (res.ok) {
        setToast({ open: true, message: `Student marked as ${status}!`, severity: 'success' });
        setSelectedStudent(null);
        fetchData();
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };

  const handleAddGrade = async () => {
    if (!addGradeForm.course_id) {
      setToast({ open: true, message: 'Please select a course', severity: 'warning' });
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/api/students/${selectedStudent.student_id}/grades`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(addGradeForm)
      });
      if (res.ok) {
        setToast({ open: true, message: 'Grade added successfully!', severity: 'success' });
        setAddGradeDialogOpen(false);
        fetchStudentTranscript(selectedStudent.student_id);
      } else {
        const err = await res.json();
        setToast({ open: true, message: `Error: ${err.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };


  const handleUpload = async () => {
    if (!uploadForm.file) {
      setToast({ open: true, message: 'Please select a file first.', severity: 'error' });
      return;
    }
    
    // For demo purposes, if selectedDemoFile is chosen, we just upload the dummy file anyway
    const formData = new FormData();
    formData.append('file', uploadForm.file);
    formData.append('course', uploadCourseInfo.courseNumber);
    formData.append('courseName', uploadCourseInfo.courseName);
    formData.append('ects', uploadCourseInfo.ects);
    formData.append('semester', uploadCourseInfo.semester);
    
    // Mapping matches the table in Step 3
    const mapping = {
      "Name": "name",
      "Full Name": "name",
      "First Name": "first_name",
      "Last Name": "last_name",
      "Vorname": "first_name",
      "Nachname": "last_name",
      "Fachsemester": "semester",
      "Semester": "semester",
      "Matrikelnr": "student_id",
      "MatrNr": "student_id",
      "Matrikelnr.": "student_id",
      "Studiengang": "program",
      "Program": "program",
      "Study Program": "program",
      "Note": "grade",
      "Grade": "grade"
    };
    formData.append('mapping', JSON.stringify(mapping));
    formData.append('nameSplitRule', nameSplitRule);
    
    try {
      const res = await fetch('http://localhost:8000/api/upload/preview/', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setPreviewData(data.preview_data);
        setActiveStep(3); // Move to Review step
      } else {
        setToast({ open: true, message: `Error: ${data.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };

  // === FINAL IMPORT CONFIRMATION (STEP 4 -> 5) ===
  /**
   * [User Story: Permanent Archive & No Partial Saves]
   * Sends the vetted, potentially edited records from the grid directly to the DB.
   * Includes atomic transaction enforcement on the backend.
   */
  const handleConfirmUpload = async () => {
    if (!gridApi) return;
    const selectedRows = gridApi.getSelectedRows();
    if (selectedRows.length === 0) {
      setToast({ open: true, message: 'No rows selected for import!', severity: 'error' });
      return;
    }
    
    const payload = {
      course: uploadCourseInfo.courseNumber,
      courseName: uploadCourseInfo.courseName,
      ects: uploadCourseInfo.ects,
      semester: uploadCourseInfo.semester,
      records: selectedRows
    };

    try {
      const res = await fetch('http://localhost:8000/api/upload/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        setToast({ open: true, message: data.message || 'Upload successful!', severity: 'success' });
        setActiveStep(4); // Move to Success step
        fetchData(); // Refresh data
      } else {
        setToast({ open: true, message: `Error: ${data.detail}`, severity: 'error' });
      }
    } catch (e) {
      setToast({ open: true, message: 'Network error', severity: 'error' });
    }
  };
  const menuItems = [
    { text: 'Teacher Dashboard', icon: <DashboardIcon /> },
    { text: 'Batch Data Upload', icon: <TableChartIcon /> },
    { text: 'Analysis Hub', icon: <SchoolIcon /> },
    { text: 'Student LSF Roster', icon: <PersonIcon /> },
  ];

  // === VIEW RENDERERS ===
  /**
   * Renders the primary Teacher Dashboard (KPIs, active cohorts).
   */
  const renderDashboard = () => (
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

  const renderUploadForm = () => {
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

  const renderCourseDetail = () => (
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

  const renderCourses = () => {
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

  const renderStudentDetail = () => (
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

  const renderStudents = () => {
    if (selectedStudent) {
      return renderStudentDetail();
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

  const renderSystemLogs = () => {
    const logs = [
      { id: 1, message: "Failed to connect to database in module data_sync.", action: "Review" },
      { id: 2, message: "Data format mismatch during import of Klausur_DBS_WS2425.", action: "Review" },
      { id: 3, message: "Authentication failure on route /api/grades.", action: "Review" },
      { id: 4, message: "Validation error: invalid grade value in results_export.", action: "Review" },
      { id: 5, message: "Timeout while fetching student roster.", action: "Review" }
    ];
    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ p: 4, maxWidth: 600 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <WarningAmberIcon color="error" sx={{ mr: 1, fontSize: 32 }} />
            <Typography variant="h5" sx={{ fontWeight: '700', color: '#D32F2F' }}>System Logs</Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 4, color: 'text.secondary' }}>Critical system errors and warnings requiring review.</Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {logs.map(log => (
              <Box key={log.id} sx={{ 
                bgcolor: 'rgba(211, 47, 47, 0.05)', 
                border: '1px solid rgba(211, 47, 47, 0.2)', 
                borderRadius: '24px', 
                p: 2, px: 3,
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between' 
              }}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="700" color="text.primary">Error Code #{log.id}00</Typography>
                  <Typography variant="body2" color="text.secondary">{log.message}</Typography>
                </Box>
                <Button variant="outlined" color="error" sx={{ borderRadius: '12px', minWidth: '100px' }}>
                  {log.action}
                </Button>
              </Box>
            ))}
          </Box>
        </Box>
      </Fade>
    );
  };

  return (
    <ThemeProvider theme={glassTheme}>

      <Dialog open={studentFormOpen} onClose={() => setStudentFormOpen(false)} PaperProps={{ sx: { borderRadius: '16px', p: 1, minWidth: 400 } }}>
        <DialogTitle sx={{ fontWeight: '800', fontSize: '1.25rem' }}>{studentFormMode === 'edit' ? 'Edit Student' : 'Create New Student'}</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" label="Student ID / Matrikelnummer" type="number" fullWidth variant="outlined" 
            value={studentForm.student_id} 
            onChange={(e) => setStudentForm({ ...studentForm, student_id: e.target.value })} 
            error={!!studentFormErrors.student_id}
            helperText={studentFormErrors.student_id}
            sx={{ mb: 2, mt: 1 }} />
          <TextField margin="dense" label="Full Name" type="text" fullWidth variant="outlined" 
            value={studentForm.name} 
            onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })} 
            error={!!studentFormErrors.name}
            helperText={studentFormErrors.name}
            sx={{ mb: 2 }} />
          <TextField margin="dense" label="Study Program" type="text" fullWidth variant="outlined" 
            value={studentForm.program} 
            onChange={(e) => setStudentForm({ ...studentForm, program: e.target.value })} 
            error={!!studentFormErrors.program}
            helperText={studentFormErrors.program}
            sx={{ mb: 2 }} />
          {studentFormMode === 'edit' && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select value={studentForm.status} label="Status" onChange={(e) => setStudentForm({ ...studentForm, status: e.target.value })}>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="graduated">Graduated</MenuItem>
                <MenuItem value="dropped">Dropped</MenuItem>
              </Select>
            </FormControl>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setStudentFormOpen(false)} color="inherit" sx={{ borderRadius: '8px' }}>Cancel</Button>
          <Button onClick={handleSaveStudent} variant="contained" color="primary" sx={{ fontWeight: '600', borderRadius: '8px' }}>Save</Button>
        </DialogActions>
      </Dialog>

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
        
        <Box component="main" sx={{ flexGrow: 1, p: 4, pt: 10, overflowY: 'auto' }}>
          
          
          {activeTab === 'Teacher Dashboard' && renderDashboard()}
          {activeTab === 'Batch Data Upload' && renderUploadForm()}
          {activeTab === 'Analysis Hub' && renderCourses()}
          {activeTab === 'Student LSF Roster' && renderStudents()}
        </Box>
      </Box>
      
      <Dialog open={courseFormOpen} onClose={() => setCourseFormOpen(false)} PaperProps={{ sx: { borderRadius: '16px', p: 1, minWidth: 400 } }}>
        <DialogTitle sx={{ fontWeight: '800', fontSize: '1.25rem' }}>{courseFormMode === 'edit' ? 'Edit Course' : 'Create New Course'}</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" label="Course Number / ID" type="text" fullWidth variant="outlined" 
            value={courseForm.course_id} 
            onChange={(e) => setCourseForm({ ...courseForm, course_id: e.target.value })} 
            error={!!courseFormErrors.course_id}
            helperText={courseFormErrors.course_id}
            sx={{ mb: 2, mt: 1 }} />
          <TextField margin="dense" label="Course Name" type="text" fullWidth variant="outlined" 
            value={courseForm.course_name} 
            onChange={(e) => setCourseForm({ ...courseForm, course_name: e.target.value })} 
            error={!!courseFormErrors.course_name}
            helperText={courseFormErrors.course_name}
            sx={{ mb: 2 }} />
          <TextField margin="dense" label="Semester" type="text" fullWidth variant="outlined" 
            value={courseForm.semester} 
            onChange={(e) => setCourseForm({ ...courseForm, semester: e.target.value })} 
            error={!!courseFormErrors.semester}
            helperText={courseFormErrors.semester}
            sx={{ mb: 2 }} />
          <TextField margin="dense" label="Study Program" type="text" fullWidth variant="outlined" 
            value={courseForm.study_program} 
            onChange={(e) => setCourseForm({ ...courseForm, study_program: e.target.value })} 
            error={!!courseFormErrors.study_program}
            helperText={courseFormErrors.study_program}
            sx={{ mb: 2 }} />
          <TextField margin="dense" label="Assigned Professor" type="text" fullWidth variant="outlined" 
            value={courseForm.professor} 
            onChange={(e) => setCourseForm({ ...courseForm, professor: e.target.value })} 
            sx={{ mb: 2 }} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setCourseFormOpen(false)} color="inherit" sx={{ borderRadius: '8px' }}>Cancel</Button>
          <Button onClick={handleSaveCourse} variant="contained" color="primary" sx={{ fontWeight: '600', borderRadius: '8px' }}>Save</Button>
        </DialogActions>
      </Dialog>


      <Dialog disableRestoreFocus disableEnforceFocus open={addGradeDialogOpen} onClose={() => setAddGradeDialogOpen(false)} PaperProps={{ sx: { borderRadius: '16px', p: 1, minWidth: 400 } }}>
        <DialogTitle sx={{ fontWeight: '800' }}>Add Manual Course Record</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Assign a new exam attempt or a new course entirely to this student's transcript.
          </Typography>
          <FormControl fullWidth variant="outlined">
            <InputLabel>Course</InputLabel>
            <Select value={addGradeForm.course_id} label="Course" onChange={(e) => setAddGradeForm({...addGradeForm, course_id: e.target.value})}>
              {coursesData.map(c => (
                <MenuItem key={c.course_id} value={c.course_id}>{c.course_name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth variant="outlined">
            <InputLabel>Semester</InputLabel>
            <Select value={addGradeForm.semester} label="Semester" onChange={(e) => setAddGradeForm({...addGradeForm, semester: e.target.value})}>
              <MenuItem value="WiSe23/24">Winter Semester 23/24</MenuItem>
              <MenuItem value="SoSe24">Summer Semester 24</MenuItem>
              <MenuItem value="WiSe24/25">Winter Semester 24/25</MenuItem>
              <MenuItem value="SoSe25">Summer Semester 25</MenuItem>
              <MenuItem value="WiSe25/26">Winter Semester 25/26</MenuItem>
            </Select>
          </FormControl>
          <TextField type="number" inputProps={{ step: 0.1, min: 1.0, max: 5.0 }} label="Grade (1.0 - 5.0)" value={addGradeForm.grade} onChange={(e) => setAddGradeForm({...addGradeForm, grade: parseFloat(e.target.value)})} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setAddGradeDialogOpen(false)} color="secondary" sx={{ fontWeight: '600' }}>Cancel</Button>
          <Button onClick={handleAddGrade} variant="contained" color="primary" sx={{ borderRadius: '12px', fontWeight: 'bold' }}>Add Record</Button>
        </DialogActions>
      </Dialog>
      
      <Snackbar open={toast.open} autoHideDuration={6000} onClose={() => setToast({...toast, open: false})}>
        <Alert severity={toast.severity} sx={{ width: '100%', borderRadius: '16px', backdropFilter: 'blur(20px)', background: toast.severity === 'success' ? 'rgba(46, 125, 50, 0.9)' : 'rgba(211, 47, 47, 0.9)', color: '#FFF' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}
