import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 1,
  iterations: 1,
};

const BASE = 'https://hotelshanmugabhavaan.com';
const LOGIN_PATH = '/api/users/login';
const ORDER_PATH = '/api/orders/';

const USERNAME = 'user@example.com'; // Replace with real user email
const PASSWORD = 'userpassword';      // Replace with real user password

export default function () {
  // Step 1: Login as user
  const loginPayload = JSON.stringify({ username: USERNAME, password: PASSWORD });
  const loginParams = { headers: { 'Content-Type': 'application/json' } };
  const loginRes = http.post(BASE + LOGIN_PATH, loginPayload, loginParams);

  check(loginRes, {
    'login status 200': (r) => r.status === 200,
    'login has access_token': (r) => {
      try { return r.json() && r.json().access_token; } catch (e) { return false; }
    },
  });

  if (loginRes.status !== 200) {
    console.log('User login failed:', loginRes.body);
    return;
  }

  const accessToken = loginRes.json().access_token;
  console.log('User access token:', accessToken);

  // Step 2: Create order (dummy payload)
  const orderPayload = JSON.stringify({
    menu_items: [
      { id: 1, qty: 2, price: 100 }, // Replace with real menu item IDs/prices
      { id: 2, qty: 1, price: 150 }
    ],
    customer_name: 'Test User',
    email: USERNAME,
    phone_number: '9999999999',
    event_type: 'Birthday',
    number_of_guests: 10,
    event_date: '2026-03-01',
    event_time: '18:00',
    address: 'Test Venue',
    payment_method: 'online',
    total_amount: 350
  });

  const orderParams = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }
  };

  const orderRes = http.post(BASE + ORDER_PATH, orderPayload, orderParams);

  check(orderRes, {
    'order status 201': (r) => r.status === 201,
    'order created': (r) => {
      try { return r.json() && r.json().order_id; } catch (e) { return false; }
    },
  });

  if (orderRes.status === 201) {
    console.log('Order created:', orderRes.json().order_id);
  } else {
    console.log('Order creation failed:', orderRes.body);
  }
}
