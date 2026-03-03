import socketio
import requests
import time
import threading

sio = socketio.Client()

@sio.event
def connect():
    print("Test Client Connected to Real Server")
    sio.emit('join', {'room': 'admins'})
    sio.emit('join', {'room': 'kitchen'})
    print("Joined rooms admins and kitchen")

@sio.on('menu_item_updated')
def on_menu_item_updated(data):
    print(">>> SUCCESS: Received menu_item_updated:", data)

sio.connect('http://127.0.0.1:8000', transports=['polling'])

def trigger_update():
    time.sleep(2)
    print("Triggering backend update...")
    l = requests.post('http://127.0.0.1:8000/api/admin/login', json={'username': 'hotelshanmugabhavaan@gmail.com', 'password': 'Admin@123'})
    token = l.json().get('access_token')
    
    r = requests.get('http://127.0.0.1:8000/api/menu')
    if r.status_code == 200 and len(r.json()) > 0:
        item_id = r.json()[0]['item_id']
        headers = {'Authorization': f'Bearer {token}'}
        u = requests.put(f'http://127.0.0.1:8000/api/menu/{item_id}', json={'stock_quantity': 105}, headers=headers)
        print('Update item response:', u.status_code)

t = threading.Thread(target=trigger_update)
t.start()

time.sleep(6)
sio.disconnect()
print("Test Complete")
