/**
 * Proxy configuration for development
 * Routes API requests to the backend server
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/chat',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: {
        '^/chat': '/chat' 
      },
      logLevel: 'silent',
    })
  );
};
