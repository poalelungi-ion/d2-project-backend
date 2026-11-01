"""
Manual smoke check for POST /api/upload/ with a multipart CSV.

Not a pytest module -- it performs a real HTTP request against a running
backend and needs `requests` installed. Run it directly:
    python tests/smoke/upload_csv.py
"""
import io
import json
import os

import requests

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:8000")
url = f'{BASE_URL}/api/upload/'

csv_data = """Matrikelnr,Name,Studiengang,Fachsemester,Note
123456,Smith, John,SE Master,3,2.0
234567,Doe, Jane,SE Master,1,1.3
345678,Johnson, Mark,Data Science Master,2,4.0
456789,Invalid, User,SE Master,1,6.0
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
    'mapping': json.dumps(mapping),
    'nameSplitRule': 'Last, First'
}

response = requests.post(url, files=files, data=data)

print(response.status_code)
print(response.json())
