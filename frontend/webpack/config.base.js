const path = require('path')
const fs = require('fs')

const postCssConfigPath = path
  .resolve(path.join(__dirname, '..', '..', 'postcss.config.js'))

const babelRc = JSON.parse(
  fs.readFileSync(
    path.resolve(
      path.join(__dirname, '..', '..', '.babelrc'),
    ),
  ),
)

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
      '../src/js/skin-default/topic-group',
    ],
    username: [
      '../src/js/skin-default/username',
    ],
    timeActualizer: [
      '../src/js/skin-default/time-actualizer',
    ],
    topicCommentListing: [
      '../src/js/skin-default/topic-comment-listing',
    ],
    topicCommentsExpansion: [
      '../src/js/skin-default/topic-comments-expansion',
    ],
    settingsPage: [
      '../src/js/skin-default/settings-page',
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
        // Transpile ES6 to ES5 everywhere except node_modules
        test: /\.js$/,
        // exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
          options: babelRc,
        }],
      },
      {
        test: /\.json$/,
        use: [{
          loader: 'json-loader',
        }],
      },
      {
        test: /\.css$/,
        use: [
          { loader: 'style-loader', options: { useable: true } },
          { loader: 'css-loader' },
          {
            loader: 'postcss-loader',
            options: { config: { path: postCssConfigPath }, sourceMap: true },
          },
        ],
      },
      {
        test: /.*\.html(\?.*)?$/,
        use: [{
          loader: 'raw-loader',
        }],
      },
    ],
  },

  // This will be extended later on from configs that inherit this
  // module
  plugins: [
  ],

  resolve: {
    modules: [
      path.resolve(__dirname, '../..'),
      path.resolve(__dirname, '../../node_modules'),
    ],
    extensions: ['.js'],
  },
  optimization: {
    runtimeChunk: 'single', // enable 'runtime.js' chunk
    usedExports: true,
    sideEffects: false,
    splitChunks: {
      chunks: 'all',
      name: 'runtime',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all',
          enforce: true,
          reuseExistingChunk: true,
        },
      },
    },
  },
}
