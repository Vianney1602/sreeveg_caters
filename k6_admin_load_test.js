import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration
export const options = {
    stages: [
        { duration: '30s', target: 20 }, // Ramp-up to 20 users over 30 seconds
        { duration: '1m', target: 20 },  // Stay at 20 users for 1 minute
        { duration: '30s', target: 0 },  // Ramp-down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
        http_req_failed: ['rate<0.01'],    // Less than 1% of requests should fail
    },
};

const BASE_URL = 'http://localhost:8000'; // Change to production URL if needed (e.g. https://api.hotelshanmugabhavaan.com)
const ADMIN_EMAIL = 'hotelshanmugabhavaan@gmail.com';
const ADMIN_PASSWORD = '_Admin_@123';

export function setup() {
    // 1. Login to get the admin token
    const loginRes = http.post(`${BASE_URL}/api/users/login`, JSON.stringify({
        email: ADMIN_EMAIL,
        password: ADMIN_PASSWORD
    }), {
        headers: { 'Content-Type': 'application/json' }
    });

    check(loginRes, {
        'logged in successfully': (r) => r.status === 200,
        'has token': (r) => r.json('token') !== undefined,
    });

    const token = loginRes.json('token');
    return { token: token };
}

export default function (data) {
    const params = {
        headers: {
            'Authorization': `Bearer ${data.token}`,
            'Content-Type': 'application/json',
        },
    };

    // 2. Hit the Admin Verification endpoint
    const verifyRes = http.get(`${BASE_URL}/api/admin/verify`, params);
    check(verifyRes, {
        'verify status is 200': (r) => r.status === 200,
    });

    sleep(1);

    // 3. Hit the Admin Stats endpoint (typically heavy as it queries orders & items)
    const statsRes = http.get(`${BASE_URL}/api/admin/stats`, params);
    check(statsRes, {
        'stats status is 200': (r) => r.status === 200,
        'has total_orders': (r) => r.json('total_orders') !== undefined,
    });

    sleep(1);

    // 4. Hit the Admin List endpoint
    const listRes = http.get(`${BASE_URL}/api/admin/list`, params);
    check(listRes, {
        'list status is 200': (r) => r.status === 200,
    });

    sleep(1);
}
