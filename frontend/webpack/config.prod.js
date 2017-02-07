const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const configBase = require('./config.base')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

const extractCSS = new ExtractTextPlugin('stylesheets/[name]-[hash:6].css')

configBase.plugins = [
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  // To split all the CSS files
  extractCSS,

  // removes a lot of debugging code in React
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production'),
    },
  }),

  new webpack.optimize.CommonsChunkPlugin({
    minChunks: 3,
    name: 'vendor',
    filename: 'vendor.bundle-[hash:6].js',
  }),

  // minifies your code
  new webpack.optimize.UglifyJsPlugin({
    compressor: {
      warnings: false,
    },
  }),
]

configBase.module.rules.push({
  test: /\.s[ac]ss$/,
  use: extractCSS.extract({
    fallback: 'style-loader',
    use: [{
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

// Override font naming in production
configBase.module.rules[0].use[0].options.name = 'fonts/[name]-[hash:6].[ext]'
configBase.module.rules[1].use[0].options.name = 'fonts/[name]-[hash:6].[ext]'

configBase.output.filename = '[name]-[hash:6].js'

module.exports = configBase
