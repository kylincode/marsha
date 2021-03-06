const webpack = require('webpack');

module.exports = {
  // Disable production-specific optimizations by default
  // They can be re-enabled by running the cli with `--mode=production` or making a separate
  // webpack config for production.
  mode: 'development',

  // Include whatwg fetch as an entry point (and not an import) as it's replacing (when necessary)
  // a globally available browser-provided function
  entry: ['./front/index.tsx'],
  output: {
    filename: 'index.js',
    path: __dirname + '/marsha/static/js',
  },

  // Enable sourcemaps for debugging webpack's output.
  devtool: 'source-map',

  resolve: {
    // Add '.ts' and '.tsx' as resolvable extensions.
    extensions: ['.ts', '.tsx', '.js', '.json'],
  },

  module: {
    rules: [
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      // All files with a '.ts' or '.tsx' extension will be handled by 'awesome-typescript-loader'.
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              babelrc: true,
            },
          },
          { loader: 'ts-loader' },
        ],
      },
      // All output '.js' files will have any sourcemaps re-processed by 'source-map-loader'.
      { enforce: 'pre', test: /\.js$/, loader: 'source-map-loader' },
    ],
  },
};
