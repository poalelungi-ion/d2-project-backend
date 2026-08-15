import os

folder = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\components\features'
files_to_fix = ['CoursesAdmin.jsx', 'StudentsAdmin.jsx', 'SystemLogs.jsx', 'BatchUploadWizard.jsx']

for file_name in files_to_fix:
    path = os.path.join(folder, file_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove the extra `};\n` that was appended at the very end
        # The last line is `};\n`, the second to last might be empty. 
        # Actually, let's just find the last `};` and remove it.
        # Wait, the script appended `\n};\n` literally. So it's the last line.
        if lines[-1].strip() == '};':
            lines = lines[:-1]
            
        # Write back
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
