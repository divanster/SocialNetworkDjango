module.exports = (middlewares, devServer) => {
  // Custom middleware setup can go here
  devServer.app.use((req, res, next) => {
    console.log(`Request URL: ${req.url}`);
    next();
  });
  return middlewares;
};
