import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 1,
  iterations: 1,
};

const BASE = 'https://hotelshanmugabhavaan.com';
const PATH = '/api/users/login';
const USERNAME = 'user@example.com'; // Replace with a real user email
const PASSWORD = 'userpassword';      // Replace with the real user password

export default function () {
  const url = `${BASE}${PATH}`;
  const payload = JSON.stringify({ username: USERNAME, password: PASSWORD });
  const params = { headers: { 'Content-Type': 'application/json' } };

  const res = http.post(url, payload, params);

  check(res, {
    'status 200': (r) => r.status === 200,
    'has access_token': (r) => {
      try { return r.json() && r.json().access_token; } catch (e) { return false; }
    },
  });

  if (res.status === 200) {
    const token = res.json().access_token;
    console.log('User access token:', token);
  } else {
    console.log('User login failed:', res.body);
  }
}
