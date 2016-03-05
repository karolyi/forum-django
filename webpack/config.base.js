var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  context: __dirname,

  entry: {
    default: [
      // entry point of our app. assets/js/index.js should require other
      // js modules and dependencies it needs
      './assets/js/skin-default/index',
    ]
  },

  output: {
    path: path.resolve(path.join(__dirname, 'assets', 'bundles/')),
    filename: '[name]-[hash].js',
  },

  plugins: [
    new BundleTracker({filename: './stats.json'}),
  ],

  module: {
    loaders: [
    // to transform JSX into JS
    {
      test: /\.jsx?$/,
      exclude: /node_modules/,
      loaders: ['react-hot', 'babel']
    }
  ],
},

  resolve: {
    modulesDirectories: [
      path.join('..', 'node_modules'),
      path.join('..', 'bower_components')
    ],
    extensions: ['', '.js', '.jsx']
  },
}
