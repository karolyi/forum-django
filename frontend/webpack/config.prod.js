const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const cleanCss = require('clean-css')

const configBase = require('./config.base')

const extractCSS = new MiniCssExtractPlugin({
  // Options similar to the same options in webpackOptions.output
  // both options are optional
  filename: 'stylesheets/[name]-[hash:6].css',
  chunkFilename: 'stylesheets/[id]-[hash:6].css',
})

const postCssConfigPath = path.resolve(
  path.join(__dirname, '..', '..', 'postcss.config.js'),
)

configBase.plugins = configBase.plugins.concat([
  new BundleTracker({
    path: __dirname,
    filename: path.join('..', 'webpack', 'stats.json'),
  }),
  // To split all the CSS files
  extractCSS,
])

// Sass compiler
configBase.module.rules.push({
  test: /\.s[ac]ss$/,
  use: [
    { loader: MiniCssExtractPlugin.loader },
    { loader: 'css-loader', options: { importLoaders: 1 } },
    {
      loader: 'postcss-loader',
      options: { config: { path: postCssConfigPath }, sourceMap: false },
    },
    {
      loader: 'sass-loader',
      options: {
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
    { loader: 'css-loader', options: { importLoaders: 1 } },
    {
      loader: 'postcss-loader',
      options: { config: { path: postCssConfigPath }, sourceMap: false },
    },
    { loader: 'stylus-loader', options: { preferPathResolver: 'webpack' } },
  ],
})

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
  minimizer: [
    // we specify a custom UglifyJsPlugin here to get source maps in production
    new TerserPlugin({
      cache: true,
      extractComments: true,
      parallel: true,
      terserOptions: {
        ecma: 8,
        // compress: true,
        compress: false,
        // mangle: true,
        mangle: false,
        output: {
          comments: false,
        },
      },
      sourceMap: false,
    }),
    // Related issue: https://github.com/cssnano/cssnano/issues/712
    new OptimizeCSSAssetsPlugin({
      cssProcessor: cleanCss,
      cssProcessorPluginOptions: {
        preset: ['default', { discardComments: { removeAll: true } }],
      },
      canPrint: true,
    }),
  ],
}
configBase.mode = 'production'

// Override font naming in production
configBase.module.rules[0].use[0].options.name = 'fonts/[name]-[hash:6].[ext]'
configBase.module.rules[1].use[0].options.name = 'fonts/[name]-[hash:6].[ext]'

configBase.output.filename = '[name]-[hash:6].js'

module.exports = configBase
