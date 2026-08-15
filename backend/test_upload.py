import requests
import io
import json

url = 'http://localhost:8000/api/upload/'

csv_data = """Matrikelnr,Name,Studiengang,Fachsemester,Note
123456,Smith, John,B.Sc. CS,3,2.0
234567,Doe, Jane,B.Sc. SE,1,1.3
345678,Johnson, Mark,M.Sc. DS,2,4.0
456789,Invalid, User,B.Sc. CS,1,6.0
"""

files = {
    'file': ('test.csv', io.StringIO(csv_data), 'text/csv')
}

mapping = {
    "Matrikelnr": "student_id",
    "Studiengang": "program",
    "Note": "grade"
}

data = {
    'course': '101',
    'courseName': 'Test Course API',
    'semester': 'WiSe23/24',
    'ects': '6',
    'mapping': json.dumps(mapping),
    'nameSplitRule': 'Last, First'
}

response = requests.post(url, files=files, data=data)

print(response.status_code)
print(response.json())
