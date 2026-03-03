import socketio
import requests
import time

sio = socketio.Client()
@sio.event
def connect():
    print("Test Client Connected to Real Server")
    sio.emit('join', {'room': 'admins'})
    sio.emit('join', {'room': 'kitchen'})

@sio.on('menu_item_updated')
def on_menu_item_updated(data):
    print("Received menu_item_updated:", data)

@sio.on('order_created')
def on_order_created(data):
    print("Received order_created:", data)

sio.connect('http://127.0.0.1:8000', transports=['polling'])
print("Waiting for emit...")
