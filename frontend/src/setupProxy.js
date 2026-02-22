const { createProxyMiddleware } = require('http-proxy-middleware');

const BACKEND = 'https://info.hotelshanmugabhavaan.com';

module.exports = function(app) {
  // Proxy API calls to production backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: BACKEND,
      changeOrigin: true,
      secure: true,
      timeout: 120000,        // 2 minute timeout
      proxyTimeout: 120000,   // 2 minute proxy timeout
      logLevel: 'warn',
      onError: (err, req, res) => {
        console.error('Proxy error:', err.message);
        if (res.writeHead) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Proxy error', message: err.message }));
        }
      },
    })
  );

  // Proxy uploaded images
  app.use(
    '/static/uploads',
    createProxyMiddleware({
      target: BACKEND,
      changeOrigin: true,
      secure: true,
      timeout: 60000,
      proxyTimeout: 60000,
      logLevel: 'warn',
    })
  );

  // NOTE: Socket.IO connects directly to BACKEND via REACT_APP_SOCKET_URL
  // Do NOT proxy /socket.io or use ws:true here — it breaks CRA's hot reload WebSocket
};
