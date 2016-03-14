/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */
'use strict'

const configBase = require('./config.base')
const webpack = require('webpack')
const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map'

configBase.output.filename = '[name].js'

configBase.plugins = [
  new webpack.ProvidePlugin({
    riot: 'riot',
  }),
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'dist', 'assets', 'stats.json'),
  }),
  new ExtractTextPlugin('[name].css'),
  // keeps hashes consistent between compilations
  new webpack.optimize.OccurenceOrderPlugin(),
  new webpack.optimize.CommonsChunkPlugin(
    /* chunkName= */'vendor', /* filename= */'vendor.bundle.js'),
]

configBase.module.loaders.push({
  test: /\.scss$/,
  loader: ExtractTextPlugin.extract(
    'style-loader', 'css-loader!sass-loader'),
})

module.exports = configBase
