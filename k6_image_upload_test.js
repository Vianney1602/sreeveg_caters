import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter, Rate } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ── Custom Metrics ──────────────────────────────────────────────────────────
const presignDuration  = new Trend('presign_duration',  true);  // ms — time to get presigned URL
const s3UploadDuration = new Trend('s3_upload_duration', true);  // ms — time to PUT image to S3
const saveItemDuration = new Trend('save_item_duration', true);  // ms — time to save menu item in DB
const totalFlowDuration = new Trend('total_flow_duration', true);// ms — full end-to-end
const uploadSuccess    = new Rate('upload_success');              // success rate
const uploadFailures   = new Counter('upload_failures');

// ── Options ─────────────────────────────────────────────────────────────────
export const options = {
  scenarios: {
    image_upload: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 3 },   // warm-up to 3 concurrent uploads
        { duration: '30s', target: 3 },   // sustained 3 concurrent uploads
        { duration: '10s', target: 0 },   // cool-down
      ],
    },
  },
  thresholds: {
    'presign_duration':    ['p(95)<2000'],   // presign under 2s at p95
    's3_upload_duration':  ['p(95)<3000'],   // S3 upload under 3s at p95
    'save_item_duration':  ['p(95)<2000'],   // DB save under 2s at p95
    'total_flow_duration': ['p(95)<5000'],   // full flow under 5s at p95
    'upload_success':      ['rate>0.95'],    // 95%+ success rate
  },
};

// ── Configuration ───────────────────────────────────────────────────────────
const DIRECT_BACKEND = 'https://info.hotelshanmugabhavaan.com';
const ADMIN_EMAIL    = 'hotelshanmugabhavaan@gmail.com';
const ADMIN_PASSWORD = '_Admin_@123';

// ── Generate a small fake JPEG (~2 KB) ──────────────────────────────────────
// k6 cannot import fs or use real files, so we create a minimal valid JPEG
// (SOI + APP0 + minimal scan data + EOI)
function generateFakeJpeg() {
  // Minimal valid JPEG: SOI marker + some filler + EOI marker
  // This is ~1 KB — enough to exercise the upload path without stressing bandwidth
  const size = 1024;
  const data = new Uint8Array(size);
  // SOI marker
  data[0] = 0xFF;
  data[1] = 0xD8;
  // JFIF APP0 marker
  data[2] = 0xFF;
  data[3] = 0xE0;
  data[4] = 0x00;
  data[5] = 0x10;
  // JFIF identifier
  data[6]  = 0x4A; // J
  data[7]  = 0x46; // F
  data[8]  = 0x49; // I
  data[9]  = 0x46; // F
  data[10] = 0x00; // null
  // Fill middle with random-ish data
  for (let i = 11; i < size - 2; i++) {
    data[i] = (i * 7 + 13) % 256;
  }
  // EOI marker
  data[size - 2] = 0xFF;
  data[size - 1] = 0xD9;
  return data.buffer;
}

// ── Setup: Login once, return token ─────────────────────────────────────────
export function setup() {
  const loginRes = http.post(
    `${DIRECT_BACKEND}/api/users/login`,
    JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(loginRes, {
    'login succeeded': (r) => r.status === 200,
    'login has token':  (r) => !!r.json('token'),
  });

  if (loginRes.status !== 200) {
    console.error(`Login failed: ${loginRes.status} — ${loginRes.body}`);
    return { token: null };
  }

  return { token: loginRes.json('token') };
}

// ── Main test function ──────────────────────────────────────────────────────
export default function (data) {
  if (!data.token) {
    console.error('No token — skipping iteration');
    uploadFailures.add(1);
    uploadSuccess.add(false);
    return;
  }

  const authHeaders = { Authorization: `Bearer ${data.token}` };
  const uniqueName  = `k6_test_item_${randomString(8)}_${__VU}_${__ITER}`;
  const fileName    = `${uniqueName}.webp`;
  const flowStart   = Date.now();
  let success       = false;
  let createdItemId = null;

  try {
    // ── Step 1: Get presigned URL ─────────────────────────────────────────
    const presignStart = Date.now();
    const presignRes   = http.get(
      `${DIRECT_BACKEND}/api/uploads/presign?filename=${encodeURIComponent(fileName)}`,
      { headers: authHeaders }
    );
    presignDuration.add(Date.now() - presignStart);

    const presignOk = check(presignRes, {
      'presign status 200':    (r) => r.status === 200,
      'presign has upload_url': (r) => !!r.json('upload_url'),
      'presign has file_url':   (r) => !!r.json('file_url'),
    });

    if (!presignOk) {
      console.error(`Presign failed: ${presignRes.status} — ${presignRes.body}`);
      uploadFailures.add(1);
      uploadSuccess.add(false);
      return;
    }

    const uploadUrl = presignRes.json('upload_url');
    const fileUrl   = presignRes.json('file_url');

    // ── Step 2: Upload fake image to S3 ───────────────────────────────────
    const fakeImage    = generateFakeJpeg();
    const s3Start      = Date.now();
    const s3Res        = http.put(uploadUrl, fakeImage);
    s3UploadDuration.add(Date.now() - s3Start);

    const s3Ok = check(s3Res, {
      's3 upload status 200': (r) => r.status === 200,
    });

    if (!s3Ok) {
      console.error(`S3 upload failed: ${s3Res.status} — ${s3Res.body}`);
      uploadFailures.add(1);
      uploadSuccess.add(false);
      return;
    }

    // ── Step 3: Save menu item with image URL ─────────────────────────────
    const payload = {
      item_name:   uniqueName,
      categories:  ['Morning Tiffin Menu'],
      price:       100,
      description: 'k6 load test item — will be deleted',
      veg:         true,
      image:       fileUrl,
    };

    const saveStart = Date.now();
    const saveRes   = http.post(
      `${DIRECT_BACKEND}/api/menu`,
      JSON.stringify(payload),
      {
        headers: {
          ...authHeaders,
          'Content-Type': 'application/json',
        },
      }
    );
    saveItemDuration.add(Date.now() - saveStart);

    const saveOk = check(saveRes, {
      'save status 200 or 201': (r) => r.status === 200 || r.status === 201,
    });

    if (!saveOk) {
      console.error(`Save failed: ${saveRes.status} — ${saveRes.body}`);
      uploadFailures.add(1);
      uploadSuccess.add(false);
      return;
    }

    // Record the created item ID for cleanup
    try {
      const body = saveRes.json();
      createdItemId = body.item_id || body.id || null;
    } catch (_) {}

    success = true;

  } finally {
    totalFlowDuration.add(Date.now() - flowStart);
    uploadSuccess.add(success);

    // ── Cleanup: delete the test item ─────────────────────────────────────
    if (createdItemId) {
      const delRes = http.del(
        `${DIRECT_BACKEND}/api/menu/${createdItemId}`,
        null,
        { headers: { ...authHeaders, 'Content-Type': 'application/json' } }
      );
      check(delRes, {
        'cleanup delete succeeded': (r) => r.status === 200,
      });
    }
  }

  sleep(1); // Pause 1s between iterations to avoid hammering the server
}

// ── Teardown ────────────────────────────────────────────────────────────────
export function teardown(data) {
  if (!data.token) return;

  // Final cleanup — fetch all menu items and delete any leftover k6 test items
  const headers = {
    Authorization: `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  const res = http.get(`${DIRECT_BACKEND}/api/menu`, { headers });
  if (res.status === 200) {
    try {
      const items = res.json();
      const testItems = items.filter(
        (item) => item.item_name && item.item_name.startsWith('k6_test_item_')
      );
      for (const item of testItems) {
        http.del(`${DIRECT_BACKEND}/api/menu/${item.item_id}`, null, { headers });
      }
      if (testItems.length > 0) {
        console.log(`Teardown: cleaned up ${testItems.length} leftover test items`);
      }
    } catch (e) {
      console.error('Teardown cleanup error:', e);
    }
  }
}
