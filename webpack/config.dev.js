var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var configBase = require('./config.base')

configBase.entry = {
  default: [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/only-dev-server',
    // entry point of our app. assets/js/index.js should require other
    // js modules and dependencies it needs
    './assets/js/skin-default/index',
    './assets/scss/skin-default/base.scss'
  ]
}

configBase.output.publicPath = 'http://localhost:3000/assets/bundles/'

configBase.plugins = [
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({filename: path.join('webpack', 'stats.json')})
]

// This turns on the creation of map files, in addition to turning on
// sourcemaps in plugins, this MUST be specified
configBase.devtool = 'source-map';

configBase.module.loaders.push({
  test: /\.scss$/,
  loaders: ['style-loader', 'css-loader?sourceMap', 'sass-loader?sourceMap']
})

module.exports = configBase;
