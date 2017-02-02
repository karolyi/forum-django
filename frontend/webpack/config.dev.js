/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */

'use strict'

const configBase = require('./config.base')
const webpack = require('webpack')
const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

const extractCSS = new ExtractTextPlugin('stylesheets/[name].css')

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map'

configBase.output.filename = '[name].js'

configBase.module.rules.push({
  test: /\.s[ac]ss$/,
  // 'to-string-loader',
  use: extractCSS.extract({
    fallbackLoader: 'style-loader',
    loader: [{
      loader: 'css-loader',
      // This should be changed to options as soon as the loader
      // supports it here.
      query: {
        sourceMap: true,
        importLoaders: 1,
      },
    }, {
      loader: 'sass-loader',
      // This should be changed to options as soon as the loader
      // supports it here.
      query: {
        sourceMap: true,
        includePaths: [
          path.resolve(__dirname, '../../node_modules'),
        ],
      },
    }],
  }),
})

configBase.plugins = [
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  extractCSS,
  // keeps hashes consistent between compilations
  // new webpack.optimize.OccurrenceOrderPlugin(),
  new webpack.optimize.CommonsChunkPlugin({
    minChunks: 3,
    name: 'vendor',
    filename: 'vendor.bundle.js',
  }),
]

module.exports = configBase
