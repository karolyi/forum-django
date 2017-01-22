/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */

'use strict'

const path = require('path')
const configBase = require('./config.base')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

let key
const tempEntry = {}

for (key of Object.keys(configBase.entry)) {
  const item = configBase.entry[key].slice()
  // Copy the original list
  // item.unshift('webpack/hot/only-dev-server')
  item.unshift('webpack/hot/dev-server')
  if (key !== 'loader') {
    // The loader doesn't get a HMR connection (everything else does)
    item.unshift('webpack-dev-server/client?http://localhost:3000/')
  }
  tempEntry[key] = item
}
configBase.entry = tempEntry

configBase.output.path = path.resolve(
  path.join(__dirname, '..', 'dist', 'assets'))
configBase.output.filename = '[name].js'
configBase.output.publicPath = 'http://localhost:3000/static/assets/'

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map'

configBase.module.rules.push({
  test: /\.scss$/,
  use: [{
    loader: 'style-loader',
    options: {
      useable: true,
    },
  }, {
    loader: 'css-loader',
    options: {
      sourceMap: true,
    },
  }, {
    loader: 'sass-loader',
    options: {
      sourceMap: true,
      includePaths: [
        path.resolve(__dirname, '../../node_modules'),
      ],
    },
  }],
})

configBase.plugins = [
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  new ExtractTextPlugin('[name].css'),
  // keeps hashes consistent between compilations, isn't needed since
  // webpack 2
  // new webpack.optimize.OccurrenceOrderPlugin(),
  new webpack.optimize.CommonsChunkPlugin({
    name: 'vendor',
    filename: 'vendor.bundle.js',
  }),
]

module.exports = configBase
