var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var configBase = require('./config.base')
var ExtractTextPlugin = require('extract-text-webpack-plugin');

configBase.plugins = [
  new BundleTracker({
    filename: path.join('./', 'webpack', 'stats.json')}),
  // To split all the CSS files
  new ExtractTextPlugin('[name].css'),

  // removes a lot of debugging code in React
  new webpack.DefinePlugin({
    'process.env': {
      'NODE_ENV': JSON.stringify('production')}}),

  // keeps hashes consistent between compilations
  new webpack.optimize.OccurenceOrderPlugin(),

  // minifies your code
  new webpack.optimize.UglifyJsPlugin({
    compressor: {
      warnings: false
    }
  })
]

configBase.module.loaders.push({
  test: /\.scss$/,
  loader: ExtractTextPlugin.extract(
    'style-loader', 'css-loader!sass-loader')
})

module.exports = configBase;
