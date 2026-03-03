from flask import Flask
from flask_socketio import SocketIO, join_room
import threading, time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('join')
def on_join(data):
    room = data.get('room')
    join_room(room)
    print(f'Client joined room {room}')

@app.route('/emit')
def trigger():
    print('Trigging emit to room admins')
    socketio.start_background_task(socketio.emit, 'my_event', {'data': 'hello'}, room='admins', namespace='/')
    return 'OK'

if __name__ == '__main__':
    socketio.run(app, port=5005)
