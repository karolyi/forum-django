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
  ]
}

configBase.output.publicPath = 'http://localhost:3000/assets/bundles/'

configBase.plugins = [
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({filename: path.join(
    'webpack', 'stats.json')}),
]

configBase.devtool = 'source-map';

configBase.module.loaders.push({
  test: /\.scss$/,
  loaders: ['style', 'css?sourceMap', 'sass?sourceMap']
})

module.exports = configBase;
