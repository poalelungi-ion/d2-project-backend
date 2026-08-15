import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Typography, FormControl, InputLabel, Select, MenuItem, TextField, Button } from '@mui/material';

export function AddGradeDialog(props) {
  const { 
    addGradeDialogOpen, setAddGradeDialogOpen, addGradeForm, setAddGradeForm, 
    coursesData, handleAddGrade 
  } = props;

  return (
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
  );
}
