import os

courses_admin = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\components\features\CoursesAdmin.jsx'
with open(courses_admin, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("import { TABS, STEPS } from '../../utils/constants';", "import { TABS, STEPS } from '../../utils/constants';\nimport { CourseDetail } from './CourseDetail';")
c = c.replace("return renderCourseDetail();", "return <CourseDetail {...props} />;")

with open(courses_admin, 'w', encoding='utf-8') as f:
    f.write(c)

students_admin = r'c:\Users\ionut\Desktop\Project\SPA_System\frontend\src\components\features\StudentsAdmin.jsx'
with open(students_admin, 'r', encoding='utf-8') as f:
    s = f.read()

s = s.replace("import { TABS, STEPS } from '../../utils/constants';", "import { TABS, STEPS } from '../../utils/constants';\nimport { StudentDetail } from './StudentDetail';")
s = s.replace("return renderStudentDetail();", "return <StudentDetail {...props} />;")

with open(students_admin, 'w', encoding='utf-8') as f:
    f.write(s)
