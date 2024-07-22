const { override, addBabelPlugins } = require('customize-cra');

const setupMiddlewares = (middlewares, devServer) => {
  devServer.app.use((req, res, next) => {
    console.log(`Request URL: ${req.url}`);
    next();
  });
  return middlewares;
};

module.exports = override(
  // Add Babel plugins with the same 'loose' mode configuration
  ...addBabelPlugins(
    ["@babel/plugin-proposal-class-properties", { "loose": true }],
    ["@babel/plugin-proposal-private-methods", { "loose": true }],
    ["@babel/plugin-proposal-private-property-in-object", { "loose": true }]
  ),
  // Add dev server middleware
  (config) => {
    config.devServer = config.devServer || {};
    config.devServer.setupMiddlewares = (middlewares, devServer) => {
      middlewares = setupMiddlewares(middlewares, devServer);
      return middlewares;
    };
    return config;
  }
);
