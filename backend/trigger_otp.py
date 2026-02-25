import requests
import json

url = "http://127.0.0.1:8000/api/users/admin/forgot-password"
payload = {"email": "hotelshanmugabhavaan@gmail.com"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
