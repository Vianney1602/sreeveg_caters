import socketio, requests, time

sio = socketio.Client()

@sio.event
def connect():
    print('Connected client')
    sio.emit('join', {'room': 'admins'})

@sio.on('my_event')
def on_my_event(data):
    print('>>> RECEIVED EVENT:', data)

sio.connect('http://127.0.0.1:5005')
time.sleep(1)

requests.get('http://127.0.0.1:5005/emit')
time.sleep(3)
sio.disconnect()
