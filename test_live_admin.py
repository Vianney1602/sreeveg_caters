import socketio
import requests
import json
import time

sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print("Admin connected to socket server via Vercel!")
    sio.emit('join', {'room': 'admins'})

@sio.on('cancellation_requested')
def on_cancel(data):
    print(">>> SUCCESS: RECEIVED CANCELLATION REQUEST:", data)

# 1. Login as Admin
l = requests.post('https://info.hotelshanmugabhavaan.com/api/admin/login', json={'username': 'hotelshanmugabhavaan@gmail.com', 'password': '_Admin_@123'}, headers={'User-Agent': 'Mozilla/5.0'})
admin_token = None
try:
    admin_token = l.json().get('access_token')
except:
    pass

if not admin_token:
    print("Failed to get admin token! Response:", l.text)
    exit(1)

print("Got Admin Token. Connecting to Socket...")

sio.connect('https://info.hotelshanmugabhavaan.com', transports=['polling'], auth={'token': admin_token})

time.sleep(15)
sio.disconnect()
