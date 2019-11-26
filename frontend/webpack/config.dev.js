/* eslint-env node */
/* eslint strict: 0, prefer-const: 1 */

'use strict'

const webpack = require('webpack')
const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

const configBase = require('./config.base')

const extractCSS = new MiniCssExtractPlugin({
  // Options similar to the same options in webpackOptions.output
  // both options are optional
  filename: 'stylesheets/[name].css',
  chunkFilename: 'stylesheets/[id].css',
})
const postCssConfigPath = path.resolve(
  path.join(__dirname, '..', '..', 'postcss.config.js'))

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map'

configBase.output.filename = '[name].js'

configBase.module.rules.push({
  test: /\.s[ac]ss$/,
  use: [
    { loader: MiniCssExtractPlugin.loader },
    { loader: 'css-loader', options: { sourceMap: true, importLoaders: 1 } },
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

// Stylus compiler
configBase.module.rules.push({
  test: /\.styl$/,
  use: [
    { loader: MiniCssExtractPlugin.loader },
    { loader: 'css-loader', options: { sourceMap: true, importLoaders: 1 } },
    {
      loader: 'postcss-loader',
      options: { config: { path: postCssConfigPath }, sourceMap: true },
    },
    {
      loader: 'stylus-loader',
      options: { sourceMap: true, preferPathResolver: 'webpack' },
    },
  ],
})

configBase.plugins = configBase.plugins.concat([
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  extractCSS,
])

configBase.optimization = {
  runtimeChunk: 'single', // enable 'runtime' chunk
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendor',
        chunks: 'all',
      },
    },
  },
}
configBase.mode = 'development'

module.exports = configBase
