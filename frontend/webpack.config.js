const setupMiddlewares = require('./src/middleware/setupMiddlewares');

module.exports = {
  // other configurations
  devServer: {
    setupMiddlewares: (middlewares, devServer) => setupMiddlewares(middlewares, devServer),
    // other devServer options
  },
};
