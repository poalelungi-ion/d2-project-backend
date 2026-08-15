import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, FormControl, InputLabel, Select, MenuItem } from '@mui/material';

export function StudentFormDialog(props) {
  const { 
    studentFormOpen, setStudentFormOpen, studentFormMode, studentForm, setStudentForm, 
    studentFormErrors, handleSaveStudent 
  } = props;

  return (
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
  );
}
