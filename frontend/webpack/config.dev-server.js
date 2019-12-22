/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */

'use strict'

const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')

const configBase = require('./config.base')

const postCssConfigPath = path
  .resolve(path.join(__dirname, '..', '..', 'postcss.config.js'))
const extractCSS = new MiniCssExtractPlugin({
  // Options similar to the same options in webpackOptions.output
  // both options are optional
  filename: 'stylesheets/[name].css',
  chunkFilename: 'stylesheets/[id].css',
})

let key
const tempEntry = {}

for (key of Object.keys(configBase.entry)) {
  const item = configBase.entry[key].slice()
  // Copy the original list
  item.unshift('webpack/hot/dev-server')
  if (key !== 'loader') {
    // The loader doesn't get a HMR connection (everything else does)
    item.unshift('webpack-dev-server/client?http://localhost:3000/')
    // item.unshift('webpack-dev-server/client?http://192.168.1.130:3000/')
    // item.unshift(`webpack-dev-server/client?http://${devHostname}:3000/`)
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
  test: /\.s[ac]ss$/,
  use: [
    { loader: 'style-loader' },
    { loader: 'css-loader', options: { sourceMap: true } },
    {
      loader: 'postcss-loader',
      options: { config: { path: postCssConfigPath }, sourceMap: true },
    },
    {
      loader: 'sass-loader',
      options: {
        sourceMap: true,
        sassOptions: {
          includePaths: [
            path.resolve(__dirname, '../../node_modules'),
          ],
        },
      },
    },
  ],
})

configBase.plugins = configBase.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  extractCSS,
])

configBase.mode = 'development'

module.exports = configBase
