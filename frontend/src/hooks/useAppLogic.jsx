import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { IconButton } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';

export function useAppLogic() {
  // === STATE DEFINITIONS & HOOKS ===
  const [themeMode, setThemeMode] = useState('light');


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


  // === VIEW RENDERERS ===
  /**
   * Renders the primary Teacher Dashboard (KPIs, active cohorts).
   */
  // Extracted AnalysisHub

  // Extracted BatchUploadWizard

  // Extracted CourseDetail

  // Extracted CoursesAdmin

  // Extracted StudentDetail

  // Extracted StudentsAdmin

  // Extracted SystemLogs


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
    setNewCourseId, studentColumnDefs, courseColumnDefs, studentRosterColumnDefs,
    toggleTheme, fetchData, fetchStudentTranscript, saveGradesToDB, openCourseForm, 
    openStudentForm, validateStudentForm, handleSaveStudent, validateCourseForm, 
    handleSaveCourse, handleUploadSubmit, updateStudentProgram, handleArchiveCourse, 
    handleStudentStatus, handleAddGrade, handleUpload, handleConfirmUpload
  };


  return appState;
}
