const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const configBase = require('./config.base')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

configBase.plugins = [
  new webpack.ProvidePlugin({
    riot: 'riot',
  }),
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
    // filename: path.join('..', 'dist', 'assets', 'stats.json'),
  }),
  // To split all the CSS files
  new ExtractTextPlugin('[name]-[hash].css'),

  // removes a lot of debugging code in React
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production'),
    },
  }),

  // keeps hashes consistent between compilations
  new webpack.optimize.OccurenceOrderPlugin(),

  new webpack.optimize.CommonsChunkPlugin(
    /* chunkName= */'vendor', /* filename= */'vendor-[hash].bundle.js'),

  // minifies your code
  new webpack.optimize.UglifyJsPlugin({
    compressor: {
      warnings: false,
    },
  }),
]

configBase.module.loaders.push({
  test: /\.scss$/,
  loader: ExtractTextPlugin.extract(
    'style-loader', 'css-loader!sass-loader'),
})

module.exports = configBase
