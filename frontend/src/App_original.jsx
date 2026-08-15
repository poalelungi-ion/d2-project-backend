import os
import re
import { ThemeProvider, createTheme } from '@mui/material/styles';
app_file = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\App.jsx'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()
  FormControl, InputLabel, Select, MenuItem, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tabs, Tab
# Chunk 1: imports
content = content.replace(
"""import {
  Box, Drawer, AppBar, CssBaseline, Toolbar, List, Typography, Divider,
  ListItem, ListItemButton, ListItemIcon, ListItemText, Button, Paper, Grid, Card, CardContent, Snackbar, Alert, Fade, Avatar,
  FormControl, InputLabel, Select, MenuItem, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tabs, Tab
} from '@mui/material';""",
"""import {
  Box, Drawer, AppBar, CssBaseline, Toolbar, List, Typography, Divider,
  ListItem, ListItemButton, ListItemIcon, ListItemText, Button, Paper, Grid, Card, CardContent, Snackbar, Alert, Fade, Avatar,
  FormControl, InputLabel, Select, MenuItem, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tabs, Tab,
  Stepper, Step, StepLabel, Badge
} from '@mui/material';""")
import ArchiveIcon from '@mui/icons-material/Archive';
# Chunk 2: Theme
old_theme = """// Professional Liquid Glass Theme with Grey, White, Black, and Uni Red
const glassTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#B71C1C' }, // Uni Red
    secondary: { main: '#424242' }, // Dark Grey
    success: { main: '#2E7D32' },
    warning: { main: '#FF8F00' },
    error: { main: '#D32F2F' },
    background: { default: 'transparent', paper: 'rgba(255, 255, 255, 0.75)' },
    text: { primary: '#212121', secondary: '#616161' }
  },
  shape: { borderRadius: 16 },
  typography: { fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.9)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.05)',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6))',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          '&:hover': {
             transform: 'translateY(-2px)',
             boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.1)',
          }
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 12,
          fontWeight: 600,
          padding: '8px 20px',
          transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
          '&:hover': { transform: 'scale(1.02)' }
        }
      }
    }
  }
});"""
          transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
new_theme = """const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#a52a2a' },
    secondary: { main: '#1A1A1A' },
    success: { main: '#2E7D32' },
    warning: { main: '#FF8F00' },
    error: { main: '#D32F2F' },
    background: { default: '#FAFAFA', paper: '#FFFFFF' },
    text: { primary: '#212121', secondary: '#616161' }
  },
  typography: { fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 8, fontWeight: 600 }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12, boxShadow: 'none', border: '1px solid rgba(0,0,0,0.1)' }
      }
    }
  }
});"""
  const [toast, setToast] = useState({ open: false, message: '', severity: 'success' });
content = content.replace(old_theme, new_theme)

# Chunk 3: state
old_state = """  const [activeTab, setActiveTab] = useState('Dashboard');
  const [coursesData, setCoursesData] = useState([]);
  const [studentsData, setStudentsData] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courseDialogOpen, setCourseDialogOpen] = useState(false);
  const [addGradeDialogOpen, setAddGradeDialogOpen] = useState(false);
  const [addGradeForm, setAddGradeForm] = useState({ course_id: '', semester: 'WiSe23/24', grade: 1.0 });
  const [archiveTab, setArchiveTab] = useState(0);
  const fetchData = async () => {
  const [newCourseName, setNewCourseName] = useState("");
  const [uploadForm, setUploadForm] = useState({ semester: '', course: '', file: null });
  const [uploadPreview, setUploadPreview] = useState(null);"""
        fetch('http://localhost:8000/api/courses/'),
new_state = """  const [activeTab, setActiveTab] = useState('Import');
  const [coursesData, setCoursesData] = useState([]);
  const [studentsData, setStudentsData] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courseDialogOpen, setCourseDialogOpen] = useState(false);
  const [addGradeDialogOpen, setAddGradeDialogOpen] = useState(false);
  const [addGradeForm, setAddGradeForm] = useState({ course_id: '', semester: 'WiSe23/24', grade: 1.0 });
  const [archiveTab, setArchiveTab] = useState(0);

  const [newCourseName, setNewCourseName] = useState("");
  const [uploadForm, setUploadForm] = useState({ semester: '', course: '', file: null });
  const [uploadPreview, setUploadPreview] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedDemoFile, setSelectedDemoFile] = useState('Klausur_DBS_WS2425.xlsx');"""
      const data = await res.json();
content = content.replace(old_state, new_state)
    } catch (e) {
# Chunk 4: menuItems
old_menu = """  const menuItems = [
    { text: 'Teacher Dashboard', icon: <DashboardIcon /> },
    { text: 'Batch Data Upload', icon: <TableChartIcon /> },
    { text: 'Course Analytics', icon: <SchoolIcon /> },
    { text: 'Student LSF Roster', icon: <PersonIcon /> },
    { text: 'Archives', icon: <ArchiveIcon /> },
  ];"""
  const saveGradesToDB = async (gridReference) => {
new_menu = """  const menuItems = [
    { text: 'Import', icon: <UploadFileIcon /> },
    { text: 'Students', icon: <PersonIcon /> },
    { text: 'Dashboard', icon: <DashboardIcon /> },
    { text: 'Activity log', badge: 3 },
  ];"""
content = content.replace(old_menu, new_menu)
      });
# Chunk 5: renderUploadForm
old_upload = content[content.find("  const renderUploadForm = () => ("):content.find("  const renderCourseDetail = () => (")]
new_upload = """  const renderUploadForm = () => {
    const steps = ['Upload file', 'Course', 'Map columns', 'Review & fix', 'Done'];
    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 4, maxWidth: 1100, margin: '0 auto', width: '100%' }}>
          <Typography variant="h4" fontWeight="800" gutterBottom sx={{ color: '#212121', mb: 1 }}>
            Import grades
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, color: '#616161', fontSize: '1rem', maxWidth: 800 }}>
            Upload a spreadsheet from any lecturer. The system standardises the columns, flags problems automatically, and only saves once everything is clean.
          </Typography>
  const handleCreateCourse = async () => {
          <Box sx={{ width: '100%', mb: 6 }}>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ '& .MuiStepLabel-label': { fontWeight: '600' }, '& .MuiStepIcon-root.Mui-active': { color: 'primary.main' } }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>
        setNewCourseName("");
          <Box
            sx={{
              border: '2px dashed rgba(0,0,0,0.15)',
              borderRadius: '16px',
              p: 8,
              textAlign: 'center',
              mb: 6,
              transition: 'all 0.3s ease',
              backgroundColor: uploadForm.file ? 'rgba(46, 125, 50, 0.04)' : '#FFFFFF',
              borderColor: uploadForm.file ? 'success.main' : 'rgba(0,0,0,0.15)',
              '&:hover': { borderColor: 'primary.main', backgroundColor: 'rgba(183, 28, 28, 0.02)' }
            }}
          >
            <input accept=".xlsx, .xls, .csv" style={{ display: 'none' }} id="excel-upload-file" type="file" onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })} />
            <label htmlFor="excel-upload-file" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ bgcolor: 'rgba(0,0,0,0.05)', borderRadius: '12px', p: 2, mb: 2, display: 'inline-flex' }}>
                 <DownloadIcon sx={{ color: '#757575', fontSize: 32 }} />
              </Box>
              <Typography variant="h6" fontWeight="700">Drag & drop .xlsx, .xls or .csv</Typography>
              <Typography variant="body2" color="text.secondary">Every lecturer's file looks different — that's fine.</Typography>
            </label>
            {uploadForm.file && <Typography variant="body1" color="success.main" fontWeight="600" sx={{ mt: 2 }}>Selected: {uploadForm.file.name}</Typography>}
          </Box>
        method: 'POST',
          <Typography variant="overline" sx={{ fontWeight: '700', color: '#9E9E9E', letterSpacing: 1, mb: 2, display: 'block' }}>
            DEMO FILES - PICK ONE TO SIMULATE AN UPLOAD
          </Typography>
        const data = await res.json();
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
                  name not split · format issues
                </Box>
              </Card>
            </Grid>
  };
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
        fetchData();
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
                  Real exam-points export — per-question point columns and no Fachsemester column, so that required field stays empty.
                </Typography>
                <Typography variant="caption" sx={{ color: '#9E9E9E', display: 'block', mb: 2, fontFamily: 'monospace', lineHeight: 1.2 }}>
                  Matrikelnr. - Last Name - First Name - Study Program - 1a - 1b - 2a - 2b - 3a - 3b - 4a - 4b - Points - Grade - Attended - Publish - Attest - Notes
                </Typography>
                <Box sx={{ bgcolor: '#FFF3E0', color: '#E65100', px: 1.5, py: 0.5, borderRadius: 1, display: 'inline-block', fontSize: '0.75rem', fontWeight: 'bold' }}>
                  missing required columns · extra point columns
                </Box>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 'auto', pt: 2 }}>
            <Button variant="contained" color="primary" size="large" sx={{ borderRadius: '8px', px: 4, fontWeight: 'bold' }}>
              Continue →
            </Button>
          </Box>
        </Box>
      </Fade>
    );
  };
"""
content = content.replace(old_upload, new_upload)
                <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: '#FF8F00' }}>{stats.kpis?.active_avg_grade || 0}</Typography>\r
# Chunk 6: layout wrapper
old_layout = content[content.find("    <ThemeProvider theme={glassTheme}>"):content.find("      <Dialog disableRestoreFocus")]
new_layout = """    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', height: '100vh', background: '#FAFAFA' }}>
        <CssBaseline />
        <AppBar position="fixed" elevation={0} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#FFFFFF', color: '#212121', borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
          <Toolbar sx={{ minHeight: '64px !important', ml: `${drawerWidth}px`, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: '700', letterSpacing: '-0.5px' }}>
              {activeTab === 'Import' ? 'Import grades' : activeTab}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Typography variant="body2" color="text.secondary" fontWeight="600">2026-06-23</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#a52a2a', fontSize: '0.9rem' }}>T</Avatar>
                <Typography variant="body2" fontWeight="600">TestUser</Typography>
              </Box>
            </Box>
          </Toolbar>
        </AppBar>
                <Box sx={{ height: 320 }}>\r
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: 'border-box',
              backgroundColor: '#1C1C1C',
              color: '#FFFFFF',
              borderRight: 'none',
              display: 'flex',
              flexDirection: 'column'
            },
          }}
        >
          <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
             <Box sx={{ bgcolor: '#a52a2a', color: '#FFF', fontWeight: 'bold', p: 1, borderRadius: 1, lineHeight: 1 }}>SSE</Box>
             <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', lineHeight: 1.2 }}>Study Progress<br/>Analysis</Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', lineHeight: 1.2 }}>Software Systems Engineering<br/>(SSE)</Typography>
             </Box>
          </Box>
                  {stats.atRisk && stats.atRisk.map((student, idx) => (\r
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)', mb: 2 }} />
                      <ListItemText \r
          <Box sx={{ overflow: 'auto', px: 2, flex: 1 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    selected={activeTab === item.text}
                    onClick={() => { setActiveTab(item.text); setSelectedStudent(null); setSelectedCourse(null); }}
                    sx={{
                      borderRadius: '8px',
                      transition: 'all 0.2s ease',
                      '&.Mui-selected': {
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        color: '#FFF',
                      },
                      '&.Mui-selected:hover': { backgroundColor: 'rgba(255,255,255,0.15)' },
                      '&:hover': { backgroundColor: 'rgba(255,255,255,0.05)' }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {item.icon && <ListItemIcon sx={{ color: activeTab === item.text ? '#FFF' : 'rgba(255,255,255,0.7)', minWidth: 40 }}>{item.icon}</ListItemIcon>}
                            <ListItemText primary={item.text} sx={{ '& .MuiTypography-root': { fontWeight: activeTab === item.text ? '600' : '400', color: activeTab === item.text ? '#FFF' : 'rgba(255,255,255,0.7)' } }} />
                        </Box>
                        {item.badge !== undefined && (
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>{item.badge}</Typography>
                        )}
                    </Box>
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
          <Typography variant="body1" sx={{ mb: 4, color: '#616161', fontSize: '1rem', maxWidth: 800 }}>\r
          <Box sx={{ p: 3, pb: 4 }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)', display: 'block' }}>Standalone tool - not linked to university systems.</Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)', display: 'block' }}>All actions are logged.</Typography>
          </Box>
        </Drawer>
              {steps.map((label) => (\r
        <Box component="main" sx={{ flexGrow: 1, p: 0, display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto' }}>
          <Toolbar sx={{ minHeight: '64px !important' }} />
          {activeTab === 'Dashboard' && renderDashboard()}
          {activeTab === 'Import' && renderUploadForm()}
          {activeTab === 'Course Analytics' && renderCourses()}
          {activeTab === 'Students' && renderStudents()}
          {activeTab === 'Activity log' && renderArchives()}
        </Box>
      </Box>
"""
content = content.replace(old_layout, new_layout)
      <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: '24px', p: 4, alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.8))' }}>
with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)
        </Typography>
print("Done")
          Select the academic semester and course, then upload the official Excel (.xlsx) file containing student grades. The system will automatically parse and validate the data.
        </Typography>

        <Card sx={{ width: '100%', maxWidth: 550, p: 4, borderRadius: 4, boxShadow: '0 12px 40px rgba(0,0,0,0.08)', border: '1px solid rgba(255,255,255,0.8)' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Academic Semester</InputLabel>
              <Select
                value={uploadForm.semester}
                label="Academic Semester"
                onChange={(e) => setUploadForm({ ...uploadForm, semester: e.target.value })}
                sx={{ borderRadius: '12px' }}
              >
                <MenuItem value="WiSe23/24">Winter Semester 23/24</MenuItem>
                <MenuItem value="SoSe24">Summer Semester 24</MenuItem>
                <MenuItem value="WiSe24/25">Winter Semester 24/25</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth variant="outlined">
              <InputLabel>Course / Subject</InputLabel>
              <Select
                value={uploadForm.course}
                label="Course / Subject"
                onChange={(e) => {
                  if (e.target.value === 'CREATE_NEW') {
                    setCourseDialogOpen(true);
                  } else {
                    setUploadForm({ ...uploadForm, course: e.target.value });
                  }
                }}
                sx={{ borderRadius: '12px' }}
              >
                {coursesData.map(c => (
                  <MenuItem key={c.course_id} value={c.course_id}>{c.course_name}</MenuItem>
                ))}
                <Divider />
                <MenuItem value="CREATE_NEW" sx={{ fontWeight: 'bold', color: '#B71C1C' }}>+ Create New Course...</MenuItem>
              </Select>
            </FormControl>

            <Box
              sx={{
                border: '2px dashed rgba(0,0,0,0.15)',
                borderRadius: '16px',
                p: 4,
                textAlign: 'center',
                transition: 'all 0.3s ease',
                backgroundColor: uploadForm.file ? 'rgba(46, 125, 50, 0.04)' : 'transparent',
                borderColor: uploadForm.file ? 'success.main' : 'rgba(0,0,0,0.15)',
                '&:hover': { borderColor: 'primary.main', backgroundColor: 'rgba(183, 28, 28, 0.02)' }
              }}
            >
              <input
                accept=".xlsx, .xls, .csv"
                style={{ display: 'none' }}
                id="excel-upload-file"
                type="file"
                onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
              />
              <label htmlFor="excel-upload-file">
                <Button variant="outlined" component="span" size="large" startIcon={<UploadFileIcon />} sx={{ mb: 2, borderRadius: '12px', borderWidth: '2px', '&:hover': { borderWidth: '2px' } }}>
                  Select File
                </Button>
              </label>
              {uploadForm.file ? (
                <Typography variant="body1" color="success.main" fontWeight="600" sx={{ mt: 1 }}>
                  Selected: {uploadForm.file.name}
                </Typography>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  No file selected. Supports .xlsx, .xls, .csv
                </Typography>
              )}
            </Box>

            <Button
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              startIcon={<SaveIcon />}
              onClick={handleUploadSubmit}
              disabled={!uploadForm.file || !uploadForm.semester || !uploadForm.course}
              sx={{ py: 1.5, borderRadius: '12px', fontSize: '1.1rem', fontWeight: '700', mt: 2, boxShadow: '0 8px 20px rgba(183, 28, 28, 0.3)' }}
            >
              Upload Data
            </Button>

            {uploadPreview && (
              <Box sx={{ mt: 2, p: 3, border: '1px solid rgba(0,0,0,0.1)', borderRadius: '12px', bgcolor: 'rgba(255,255,255,0.5)' }}>
                <Typography variant="h6" fontWeight="700" sx={{ mb: 2 }}>Data Preview</Typography>
                <div className="ag-theme-alpine" style={{ height: 200, width: '100%' }}>
                  <AgGridReact
                    rowData={uploadPreview}
                    columnDefs={[
                      { field: 'student_id', headerName: 'Student ID' },
                      { field: 'grade', headerName: 'Grade' },
                      { field: 'passed', headerName: 'Passed' }
                    ]}
                  />
                </div>
                <Button variant="outlined" color="secondary" fullWidth sx={{ mt: 2 }} onClick={() => setUploadPreview(null)}>Dismiss Preview</Button>
              </Box>
            )}
          </Box>
        </Card>
      </Paper>
    </Fade>
  );

  const renderCourseDetail = () => (
    <Fade in={true} timeout={800}>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ mb: 3 }}>
          <Button startIcon={<ChevronLeftIcon />} onClick={() => setSelectedCourse(null)} sx={{ color: '#424242', mb: 1 }}>Return to List</Button>
          <Typography variant="h3" sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>{selectedCourse.course_name}</Typography>
          <Box sx={{ display: 'flex', gap: 3, mt: 1, flexWrap: 'wrap' }}>
            <Typography variant="h6" sx={{ color: '#616161', fontWeight: '400' }}>Average Grade: <strong>{selectedCourse.avg_grade}</strong></Typography>
            <Typography variant="h6" sx={{ color: '#616161', fontWeight: '400' }}>Pass Rate: <strong style={{color: selectedCourse.pass_rate > 50 ? '#2E7D32' : '#D32F2F'}}>{selectedCourse.pass_rate}%</strong></Typography>
            <Typography variant="h6" sx={{ color: '#616161', fontWeight: '400' }}>Total Submissions: <strong>{selectedCourse.total_attempts}</strong></Typography>
            {!selectedCourse.is_archived && (
               <Button variant="outlined" color="secondary" startIcon={<ArchiveIcon />} onClick={() => handleArchiveCourse(selectedCourse.course_id, true)} sx={{ ml: 'auto', borderRadius: '8px' }}>Archive Course</Button>
            )}
            {selectedCourse.is_archived && (
               <Button variant="outlined" color="primary" startIcon={<RestoreIcon />} onClick={() => handleArchiveCourse(selectedCourse.course_id, false)} sx={{ ml: 'auto', borderRadius: '8px' }}>Restore Course</Button>
            )}
          </Box>
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
          <div className="ag-theme-alpine" style={{ flex: 1, width: '100%', padding: '16px' }}>
            <AgGridReact
              ref={courseGridRef}
              rowData={selectedCourse.marks}
              columnDefs={[
                { field: 'student_id', headerName: 'Student ID', flex: 1 },
                { field: 'student_name', headerName: 'Name', flex: 2 },
                { field: 'semester', headerName: 'Semester', flex: 1 },
                { field: 'grade', headerName: 'Grade', flex: 1, type: 'numericColumn', cellStyle: { fontWeight: 'bold' } },
                { field: 'passed', headerName: 'Passed?', flex: 1, cellRenderer: params => params.value ? 'Yes' : 'No' }
              ]}
              defaultColDef={{ resizable: true, sortable: true, filter: true }}
              animateRows={true}
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

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
             <Box>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px', m: 0 }}>Course Analytics</Typography>
                <Typography variant="h6" sx={{ color: '#616161', fontWeight: '400', mt: 1 }}>Performance metrics broken down per course offering. Click a course to see detailed marks.</Typography>
             </Box>
             <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setCourseDialogOpen(true)} sx={{ borderRadius: '12px', height: 48, px: 3, boxShadow: '0 8px 20px rgba(183, 28, 28, 0.3)' }}>Create New Course</Button>
          </Box>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {coursesData.filter(c => !c.is_archived).map(course => (
              <Grid item xs={12} md={6} lg={4} key={course.course_id}>
                <Card sx={{ cursor: 'pointer' }} onClick={() => setSelectedCourse(course)}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: '700', mb: 2 }}>{course.course_name}</Typography>
                    <Divider sx={{ mb: 2, opacity: 0.5 }} />
                    <Typography variant="body1" sx={{display: 'flex', justifyContent: 'space-between', mb: 1}}>
                      Total Submissions: <strong>{course.total_attempts}</strong>
                    </Typography>
                    <Typography variant="body1" sx={{display: 'flex', justifyContent: 'space-between', mb: 1}}>
                      Pass Rate: <strong style={{color: course.pass_rate > 50 ? '#2E7D32' : '#D32F2F'}}>{course.pass_rate}%</strong>
                    </Typography>
                    <Typography variant="body1" sx={{display: 'flex', justifyContent: 'space-between'}}>
                      Average Grade: <strong>{course.avg_grade}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
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
            <Typography variant="h6" sx={{ color: '#616161', fontWeight: '400' }}>ID: {selectedStudent.student_id}</Typography>
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
            <AgGridReact ref={studentGridRef} rowData={selectedStudent.transcript} columnDefs={studentColumnDefs} defaultColDef={{ resizable: true, sortable: true, filter: true }} animateRows={true} />
          </div>
        </Paper>
      </Box>
    </Fade>
  );

  const renderStudents = () => {
    if (selectedStudent) {
      return renderStudentDetail();
    }

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>LSF Student Roster</Typography>
          <Typography variant="h6" sx={{ mb: 4, color: '#616161', fontWeight: '400' }}>Select any student to view and edit their specific attempts and marks.</Typography>
          <Grid container spacing={3}>
            {studentsData.filter(s => s.status === 'active').map(student => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={student.student_id}>
                <Card sx={{ cursor: 'pointer', border: student.program === 'Unknown' ? '2px solid #FF8F00' : 'none', position: 'relative' }} onClick={() => fetchStudentTranscript(student.student_id)}>
                  {student.program === 'Unknown' && (
                     <Box sx={{ position: 'absolute', top: 12, right: 12, color: '#FF8F00' }}>
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
                       <Typography variant="body2" sx={{color: '#616161'}}>Exams: <strong>{student.total_exams}</strong></Typography>
                       <Typography variant="body2" sx={{color: '#616161'}}>Avg: <strong>{student.avg_grade}</strong></Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Fade>
    );
  };

  const renderArchives = () => {
    if (selectedCourse) return renderCourseDetail();
    if (selectedStudent) return renderStudentDetail();

    const archivedCourses = coursesData.filter(c => c.is_archived);
    const graduatedStudents = studentsData.filter(s => s.status === 'graduated');
    const failedStudents = studentsData.filter(s => s.status === 'failed');

    return (
      <Fade in={true} timeout={800}>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h3" gutterBottom sx={{ fontWeight: '800', letterSpacing: '-1.5px' }}>Archives</Typography>
          <Typography variant="h6" sx={{ mb: 4, color: '#616161', fontWeight: '400' }}>View archived courses, graduated alumni, and failed out students.</Typography>

          <Paper sx={{ mb: 4, borderRadius: '16px', border: '1px solid rgba(0,0,0,0.05)', overflow: 'hidden' }}>
            <Tabs
              value={archiveTab}
              onChange={(e, newValue) => setArchiveTab(newValue)}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
              sx={{ '& .MuiTab-root': { fontWeight: '700', fontSize: '1rem', py: 2, textTransform: 'none' } }}
            >
              <Tab icon={<ArchiveIcon />} iconPosition="start" label={`Archived Courses (${archivedCourses.length})`} />
              <Tab icon={<CheckCircleIcon />} iconPosition="start" label={`Graduated Alumni (${graduatedStudents.length})`} />
              <Tab icon={<CancelIcon />} iconPosition="start" label={`Failed Students (${failedStudents.length})`} />
            </Tabs>
          </Paper>

          {archiveTab === 0 && (
            <Grid container spacing={3}>
              {archivedCourses.map(course => (
                <Grid item xs={12} md={6} lg={4} key={course.course_id}>
                  <Card sx={{ opacity: 0.8, cursor: 'pointer' }} onClick={() => setSelectedCourse(course)}>
                    <CardContent sx={{ p: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: '700', mb: 2 }}>{course.course_name}</Typography>
                      <Divider sx={{ mb: 2, opacity: 0.5 }} />
                      <Typography variant="body2" color="text.secondary">Total Submissions: {course.total_attempts}</Typography>
                      <Typography variant="body2" color="text.secondary">Pass Rate: {course.pass_rate}%</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {archivedCourses.length === 0 && <Typography variant="body1" sx={{ ml: 2, color: 'text.secondary', width: '100%', textAlign: 'center', mt: 4 }}>No archived courses.</Typography>}
            </Grid>
          )}

          {archiveTab === 1 && (
            <Grid container spacing={3}>
              {graduatedStudents.map(student => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={student.student_id}>
                  <Card sx={{ border: '2px solid #2E7D32', opacity: 0.9, cursor: 'pointer' }} onClick={() => fetchStudentTranscript(student.student_id)}>
                    <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Avatar sx={{ width: 64, height: 64, bgcolor: '#2E7D32', mb: 2 }}><CheckCircleIcon fontSize="large" /></Avatar>
                      <Typography variant="h6" sx={{ fontWeight: '700', textAlign: 'center' }}>{student.name}</Typography>
                      <Typography variant="body2" sx={{ color: '#2E7D32', mb: 1, fontWeight: '600' }}>{student.student_id}</Typography>
                      <Typography variant="body2" sx={{ color: '#616161' }}>{student.program}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {graduatedStudents.length === 0 && <Typography variant="body1" sx={{ ml: 2, color: 'text.secondary', width: '100%', textAlign: 'center', mt: 4 }}>No graduated students.</Typography>}
            </Grid>
          )}

          {archiveTab === 2 && (
            <Grid container spacing={3}>
              {failedStudents.map(student => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={student.student_id}>
                  <Card sx={{ border: '2px solid #D32F2F', opacity: 0.9, cursor: 'pointer' }} onClick={() => fetchStudentTranscript(student.student_id)}>
                    <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Avatar sx={{ width: 64, height: 64, bgcolor: '#D32F2F', mb: 2 }}><CancelIcon fontSize="large" /></Avatar>
                      <Typography variant="h6" sx={{ fontWeight: '700', textAlign: 'center' }}>{student.name}</Typography>
                      <Typography variant="body2" sx={{ color: '#D32F2F', mb: 1, fontWeight: '600' }}>{student.student_id}</Typography>
                      <Typography variant="body2" sx={{ color: '#616161' }}>{student.program}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {failedStudents.length === 0 && <Typography variant="body1" sx={{ ml: 2, color: 'text.secondary', width: '100%', textAlign: 'center', mt: 4 }}>No failed students.</Typography>}
            </Grid>
          )}
        </Box>
      </Fade>
    );
  };

  return (
    <ThemeProvider theme={glassTheme}>
      <Box sx={{ display: 'flex', height: '100vh', background: 'transparent' }}>
        <CssBaseline />
