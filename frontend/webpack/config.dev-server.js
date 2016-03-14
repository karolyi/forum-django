/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */
'use strict'

const path = require('path')
const configBase = require('./config.base')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')

const tempEntry = {}
for (let key of Object.keys(configBase.entry)) {
  const item = configBase.entry[key].slice()
  // Copy the original list
  item.unshift('webpack/hot/only-dev-server')
  if (key !== 'loader') {
    // The loader doesn't get a HMR connection (everything else does)
    item.unshift('webpack-dev-server/client?http://localhost:8081')
  }
  tempEntry[key] = item
}
configBase.entry = tempEntry

configBase.output.path = path.resolve(
  path.join(__dirname, '..', 'src', 'assets'))
configBase.output.filename = '[name].js'
configBase.output.publicPath = '/assets/'

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map'

configBase.module.loaders.push({
  test: /\.scss$/,
  loaders: ['style-loader', 'css-loader?sourceMap', 'sass-loader?sourceMap'],
})

configBase.plugins = [
  new webpack.ProvidePlugin({
    riot: 'riot',
  }),
  new webpack.HotModuleReplacementPlugin(),
  // new webpack.NoErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'dist', 'assets', 'stats.json'),
  }),
]


module.exports = configBase
