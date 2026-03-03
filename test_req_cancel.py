import requests

l = requests.post('https://info.hotelshanmugabhavaan.com/api/admin/login', json={'username': 'hotelshanmugabhavaan@gmail.com', 'password': '_Admin_@123'}, headers={'User-Agent': 'Mozilla'})
token = l.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'Mozilla'}

r = requests.get('https://info.hotelshanmugabhavaan.com/api/orders', headers=headers)
orders = r.json()
valid_order = next((o for o in orders if o['status'].lower() not in ['delivered', 'cancelled']), None)

if valid_order:
    print(f"Requesting cancellation for order {valid_order['order_id']}")
    c = requests.post(f'https://info.hotelshanmugabhavaan.com/api/orders/{valid_order["order_id"]}/request-cancel', headers=headers)
    print(c.status_code, c.text)
else:
    print("No valid orders to cancel")
