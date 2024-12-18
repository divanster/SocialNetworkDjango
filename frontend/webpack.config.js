const path = require('path');

module.exports = {
  // Define entry point
  entry: './src/index.tsx',

  // Define output
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'bundle.js',
    publicPath: '/',
  },

  // Module rules to handle different file types
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: 'ts-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[hash].[ext]',
              outputPath: 'images',
            },
          },
        ],
      },
    ],
  },

  // Resolve extensions
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    fallback: {
      process: require.resolve('process/browser'), // Polyfill process for browser environment
    },
  },

  // DevServer configuration
  devServer: {
    contentBase: path.join(__dirname, 'public'),
    historyApiFallback: true,
    hot: true,
  },

  // Plugins (optional, if needed for further customization)
  plugins: [
    // Add any other necessary plugins here
  ],
};
