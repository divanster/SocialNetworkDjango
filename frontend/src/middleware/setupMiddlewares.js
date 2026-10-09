module.exports = (middlewares, devServer) => {
  devServer.app.use((_req, _res, next) => {
    next();
  });
  return middlewares;
};
