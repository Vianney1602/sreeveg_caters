const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function test() {
  const fd = new FormData();
  fd.append('image', Buffer.from('89504E470D0A1A0A', 'hex'), {
    filename: 'dummy.png',
    contentType: 'image/png',
  });
  
  try {
    const res = await axios.post('https://info.hotelshanmugabhavaan.com/api/uploads/image', fd, {
      headers: {
        ...fd.getHeaders() // Node's form-data requires this, but browser's FormData doesn't!
      }
    });
    console.log(res.status, res.data);
  } catch (err) {
    if (err.response) {
      console.error(err.response.status, err.response.data);
    } else {
      console.error(err.message);
    }
  }
}
test();
