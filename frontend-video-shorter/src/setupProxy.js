// frontend-video-shorter/src/setupProxy.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy for /api/me (which is already correctly prefixed on backend)
  app.use(
    '/api/me', // Specific path, no rewrite needed if backend has /api/me
    createProxyMiddleware({
      target: 'http://localhost:8000', 
      changeOrigin: true,
    })
  );

  // Proxy for other /api calls like /api/create_clip, /api/generate_highlights
  // These need the /api prefix removed when forwarding to the backend.
  app.use(
    '/api', // Catches /api/* (ensure this is ordered correctly if more specific /api routes are added above)
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '', // Remove /api prefix
      },
    })
  );
};
