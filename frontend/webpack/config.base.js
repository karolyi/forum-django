const path = require('path')

module.exports = {
  context: __dirname,

  entry: {
    loader: [
      '../src/js/loader',
    ],
    common: [
      // Put the JS entries always at the end, otherwise libraryTarget
      // variable exportin will not work!
      '../src/scss/skin-default/base.scss',
      '../src/js/skin-default/common',
    ],
    topicGroup: [
      '../src/js/skin-default/topicGroup',
    ],
  },

  output: {
    path: path.resolve(path.join(__dirname, '..', 'dist', 'assets')),
    publicPath: '/static/assets/',
    filename: '[name]-[hash].js',
    // http://stackoverflow.com/questions/34357489/calling-webpacked-code-from-outside-html-script-tag
    libraryTarget: 'var',
    library: ['Forum', '[name]'],
  },

  // configure your plugins at the separate mode level files

  module: {
    loaders: [
      {
        // Transpile ES6 to ES5
        test: /\.js?$/,
        exclude: /node_modules/,
        loaders: ['babel'],
      },
      // to transform JSX into JS
      // {
      //   test: /\.jsx?$/,
      //   exclude: /node_modules/,
      //   loaders: ['react-hot', 'babel']
      // },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'url?limit=10000&mimetype=application/font-woff',
      },
      {
        test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'file-loader',
      },
    ],
  },

  urlLoader: {
    limit: 10000,
    mimetype: 'application/font-woff',
  },

  resolveUrlLoader: {
    root: '/assets/',
  },

  sassLoader: {
    includePaths: [
      path.resolve(__dirname, '../../node_modules'),
    ],
  },

  resolve: {
    modulesDirectories: [
      'node_modules',
      'bower_components',
    ],
    extensions: ['', '.js'],
  },
}
