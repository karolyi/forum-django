var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  context: __dirname,

  entry: {
    default: [
      // entry point of our app. assets/js/index.js should require other
      // js modules and dependencies it needs
      './assets/js/skin-default/index',
      './assets/scss/skin-default/base.scss',
    ]
  },

  output: {
    path: path.resolve(path.join(__dirname, 'assets', 'bundles/')),
    filename: '[name]-[hash].js',
  },

  plugins: [
    new BundleTracker({filename: './stats.json'}),
    new ExtractTextPlugin('[name].css')
  ],

  module: {
    loaders: [
      // to transform JSX into JS
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loaders: ['react-hot', 'babel']
      },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'url-loader?limit=10000&mimetype=application/font-woff'
      },
      {
        test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'file-loader'
      }
    ],
  },

  sassLoader: {
    includePaths: [
      path.resolve(__dirname, '../node_modules')
    ]
  },

  resolve: {
    modulesDirectories: [
      'node_modules',
      'bower_components'
    ],
    extensions: ['', '.js', '.jsx']
  },
}
