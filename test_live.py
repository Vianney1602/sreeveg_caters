import socketio
import requests
import time

sio = socketio.Client(logger=True, engineio_logger=True)
@sio.event
def connect():
    print("Connected to Live Server!")
    sio.emit('join', {'room': 'admins'})
    print("Requested to join admins")

@sio.on('cancellation_requested')
def on_cancel(data):
    print("RECEIVED LIVE CANCEL", data)

@sio.event
def disconnect():
    print("Disconnected from Live Server")

print("connecting...")
try:
    sio.connect('https://info.hotelshanmugabhavaan.com', transports=['polling'])
    time.sleep(5)
    sio.disconnect()
except Exception as e:
    print("Error connecting:", e)
