import os
import re

components_dir = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\components\features'
app_file = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\App.jsx'

correct_vars = """    themeMode, setThemeMode, activeTab, setActiveTab, coursesData, setCoursesData,
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
    handleStudentStatus, handleAddGrade, handleUpload, handleConfirmUpload"""

def fix_app_jsx():
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex to replace the appState content
    pattern = r'(const appState = \{).*?(\n  \};)'
    new_appState = r'\1\n' + correct_vars + r'\2'
    content = re.sub(pattern, new_appState, content, flags=re.DOTALL)
    
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_components():
    for f_name in os.listdir(components_dir):
        if not f_name.endswith('.jsx'): continue
        path = os.path.join(components_dir, f_name)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # regex to replace the destructured props
        pattern = r'(const \{\s*).*?(\s*\} = props;)'
        new_props = r'\1' + correct_vars + r'\2'
        content = re.sub(pattern, new_props, content, flags=re.DOTALL)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

fix_app_jsx()
fix_components()
