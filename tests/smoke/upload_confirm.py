"""
Manual smoke check for POST /api/upload/confirm/.

Not a pytest module -- it performs a real HTTP request against a running
backend. Run it directly:  python tests/smoke/upload_confirm.py
"""
import json
import os
import urllib.request

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:8000")

payload = {
    "course": "TEST101",
    "courseName": "Test Course",
    "ects": "6",
    "semester": "WISE_25",
    "records": [
        {
            "student_id": "9999",
            "first_name": "Test",
            "last_name": "Student",
            "name": "Test Student",
            "program": "Test Program",
            "semester": "WISE_25",
            "grade": "1.0"
        }
    ]
}

req = urllib.request.Request(
    f'{BASE_URL}/api/upload/confirm/',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
