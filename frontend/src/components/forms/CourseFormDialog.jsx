import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button } from '@mui/material';

export function CourseFormDialog(props) {
  const { 
    courseFormOpen, setCourseFormOpen, courseFormMode, courseForm, setCourseForm, 
    courseFormErrors, handleSaveCourse 
  } = props;

  return (
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
  );
}
