const path = require('path')

module.exports = {
  context: __dirname,

  entry: {
    loader: [
      '../src/js/loader',
    ],
    common: [
      // Put the JS entries always at the end, otherwise libraryTarget
      // variable exporting will not work!
      '../src/scss/skin-default/base.scss',
      '../src/js/skin-default/common',
    ],
    topicGroup: [
      '../src/js/skin-default/topicGroup',
    ],
    userName: [
      '../src/js/skin-default/userName',
    ],
    timeActualizer: [
      '../src/js/skin-default/timeActualizer',
    ],
    topicCommentListing: [
      '../src/js/skin-default/topicCommentListing',
    ],
    topicCommentsExpansion: [
      '../src/js/skin-default/topicCommentsExpansion',
    ],
    settingsPage: [
      '../src/js/skin-default/settingsPage',
    ],
  },

  output: {
    path: path.resolve(path.join(__dirname, '..', 'dist', 'assets')),
    publicPath: '/static/assets/',
    filename: '[name].js',
    // http://stackoverflow.com/questions/34357489/calling-webpacked-code-from-outside-html-script-tag
    libraryTarget: 'var',
    library: ['Forum', '[name]'],
  },

  // configure your plugins at the separate mode level files
  module: {
    rules: [
      // Keep this at 1st place, prod settings modify this
      {
        test: /\.(ttf|eot|svg|woff)(\?.*)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            name: 'fonts/[name].[ext]',
          },
        }],
      },
      // Keep this at 2nd place, prod settings modify this
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [{
          loader: 'url-loader',
          options: {
            limit: 10000,
            mimetype: 'application/font-woff',
            name: 'fonts/[name].[ext]',
          },
        }],
      },
      {
        // Transpile ES6 to ES5
        test: /\.js?$/,
        exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
          options: {
            babelrc: true,
          },
        }],
      },
      {
        // Transpile ES6 to ES5 in Bootstrap V4
        test: /bootstrap\/js\/src\/.*\.js$/,
        use: [{
          loader: 'imports-loader',
          options: {
            jQuery: 'jquery',
          },
        }, {
          loader: 'babel-loader',
          options: {
            babelrc: true,
          },
        }],
      },
      {
        // Transpile ES6 to ES5 in Bootstrap V4
        test: /bootstrap\/js\/src\/tooltip.js$/,
        use: [{
          loader: 'imports-loader',
          options: {
            jQuery: 'jquery',
            Tether: 'tether',
          },
        }, {
          loader: 'babel-loader',
          options: {
            babelrc: true,
          },
        }],
      },
      { test: /\.json$/,
        use: [{
          loader: 'json-loader',
        }],
      },
      {
        test: /\.css$/,
        // loaders: ['style-loader', 'css-loader'],
        use: [{
          loader: 'style-loader',
          options: {
            useable: true,
          },
        }, {
          loader: 'css-loader',
        }],
      },
      {
        test: /pen\/src\/pen.js$/,
        use: [{
        //   loader: 'imports-loader',
        //   options: {
        //     window: 'this',
        //   },
        // }, {
          loader: 'exports-loader',
          options: {
            Pen: 'window.Pen',
          },
        }],
      },
    ],
  },

  resolve: {
    modules: [
      'node_modules',
    ],
    extensions: ['.js'],
  },
}
