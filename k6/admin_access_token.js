import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 1,
  iterations: 1,
};

const BASE = 'https://hotelshanmugabhavaan.com';
const PATH = '/api/admin/login';
const USERNAME = 'hotelshanmugabhavaan@gmail.com';
const PASSWORD = '_Admin_@123';

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
    console.log('Admin access token:', token);
  } else {
    console.log('Admin login failed:', res.body);
  }
}
